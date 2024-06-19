import pathlib
import yaml
import os
import asyncio
import asyncpg
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI = AsyncOpenAI()


async def get_embedding(input: str):
    return (
        (
            await OPENAI.embeddings.create(
                input=input, model="text-embedding-3-large", dimensions=3072
            )
        )
        .data[0]
        .embedding
    )


async def main():
    embedding_3_large = {}
    try:
        with open(
            pathlib.Path(".") / "embedding" / "embedding_3_large.yaml",
            "r",
            encoding="utf-8",
        ) as f:
            embedding_3_large = yaml.safe_load(f)
    except Exception as ex:
        print(ex)
    conn = await asyncpg.connect(
        dsn=os.environ.get("DATABASE_URL"),
    )
    knowledge = {}
    for file in pathlib.Path("./knowledge").glob("**/*.yaml"):
        with open(file, "r", encoding="utf-8") as f:
            for i in yaml.safe_load(f) or []:
                if i["name"] in embedding_3_large:
                    continue
                knowledge[i["name"]] = i
    for key in knowledge:
        print(f"{key}")
        await conn.execute(
            (
                "INSERT INTO manim_embedding (vec, name) VALUES ($1, $2) "
                "ON CONFLICT (name) DO UPDATE SET vec = $1"
            ),
            str(await get_embedding(knowledge[key]["content"])),
            f"{key}-content",
        )
        if "description" in knowledge[key]:
            await conn.execute(
                (
                    "INSERT INTO manim_embedding (vec, name) VALUES ($1, $2) "
                    "ON CONFLICT (name) DO UPDATE SET vec = $1"
                ),
                str(await get_embedding(knowledge[key]["description"])),
                f"{key}-description",
            )
        embedding_3_large[key] = []

    with open(
        pathlib.Path(".") / "embedding" / "embedding_3_large.yaml",
        "w",
        encoding="utf-8",
    ) as f:
        yaml.dump(embedding_3_large, f)
    await conn.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
