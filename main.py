import os
import pathlib
from json import loads
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from markdown import markdown
from sanic import Sanic
from sanic.request import Request
from sanic.response import html
from sanic.response import json
from dotenv import load_dotenv


from database import aquery

load_dotenv()
app = Sanic(name="manim-gpt")
try:
    with open("./readme.md", "r", encoding="utf-8") as f:
        INDEX_PAGE = markdown(f.read())
except Exception as ex:
    INDEX_PAGE = markdown("# Error loading readme.md\n\n" + str(ex))
OPENAI = AsyncOpenAI()


@app.route("/")
async def home(request: Request):
    return html(INDEX_PAGE)


async def get_data(query: str):
    embedding = await OPENAI.embeddings.create(
        model="text-embedding-3-large",
        input=query,
        dimensions=3072,
    )
    return await aquery(
        embedding=embedding.data[0].embedding,
    )


@app.route("/v1/chat/completions", methods=["POST"])
async def chat_completions(request: Request):
    # get auth token from header
    auth_token: str = request.headers.get("Authorization")
    if not auth_token.startswith("Bearer "):
        return json({"error": "Unauthorized"}, status=401)
    if auth_token[7:] != os.environ.get("AUTH_TOKEN"):
        return json({"error": "Unauthorized"}, status=401)
    body = request.json
    if body["model"] != "manim-gpt":
        return json({"error": "Unauthorized"}, status=401)
    body["model"] = "bot-chat"
    if "stream" in body:
        del body["stream"]

    msgs = body["messages"].copy()
    msgs.append(
        {
            "role": "system",
            "content": "请你根据上面的内容，生成RAG查询。只需要生成查询的内容就行，例如“生成坐标轴”",
        }
    )
    msgs.append(
        {
            "role": "user",
            "content": "请你根据上面的内容，生成RAG查询。只需要生成查询的内容就行，例如“生成坐标轴”",
        }
    )

    rsp = await OPENAI.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=msgs,
    )
    query = rsp.choices[0].message.content
    r = ""
    for i, s in enumerate(await get_data(query)):
        r += f"{i+1}:\n{s}\n\n"

    body["messages"].append(
        {
            "role": "user",
            "content": f"""<Query>
{query}
</Query>

<Result>
{r}
</Result>

请根据上面的内容，再做出回答。""",
        },
    )
    return json((await OPENAI.chat.completions.create(**body)).model_dump())


if __name__ == "__main__":
    app.run(
        host="::",
        port=int(os.environ.get("LISTEN_PORT", 8080)),
        ssl={"cert": "./cert.pem", "key": "./key.pem"},
    )
