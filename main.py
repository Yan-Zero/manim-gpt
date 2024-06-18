import os
from markdown import markdown
from sanic import Sanic
from sanic.request import Request
from sanic.response import html
from dotenv import load_dotenv

load_dotenv()
app = Sanic(name="manim-gpt")
try:
    with open("./readme.md", "r", encoding="utf-8") as f:
        INDEX_PAGE = markdown(f.read())
except Exception as ex:
    INDEX_PAGE = markdown("# Error loading readme.md\n\n" + str(ex))


@app.route("/")
async def home(request: Request):
    return html(INDEX_PAGE)


@app.route("/v1/chat/completions", methods=["POST"])
async def chat_completions(request: Request):
    return markdown("# Not Finished")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("LISTEN_PORT", 8080)))
