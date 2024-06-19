import yaml
import os
import pathlib
import asyncpg

KNOWLEDGE = {}
for file in pathlib.Path("./knowledge").glob("**/*.yaml"):
    with open(file, "r", encoding="utf-8") as f:
        for i in yaml.safe_load(f) or []:
            KNOWLEDGE[i["name"]] = i

conn = None


async def aquery(embedding: list[float], top_k: int = 6) -> list[str]:
    conn = await asyncpg.connect(os.environ.get("DATABASE_URL"))
    data = []
    for i in await conn.fetch(
        ("SELECT name FROM manim_embedding ORDER BY vec <#> $1 LIMIT $2;"),
        str(embedding),
        top_k * 2,
    ):
        name = i["name"].rsplit("-", 1)[0]
        if name not in KNOWLEDGE:
            continue
        if name in data:
            continue
        data.append(name)
    data = data[:top_k]
    print(data)
    await conn.close()
    return [KNOWLEDGE[i]["content"] for i in data]
