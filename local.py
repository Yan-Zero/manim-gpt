import pathlib
import yaml
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


if __name__ == "__main__":
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

    if not isinstance(embedding_3_large, dict):
        embedding_3_large = {}

    client = OpenAI()

    def get_embedding(text: str):
        return client.embeddings.create(
            model="text-embedding-3-large",
            input=text,
            dimensions=3072,
        ).data[0]

    knowledge_dict = []
    for file in pathlib.Path("./knowledge").glob("**/*.yaml"):
        with open(file, "r", encoding="utf-8") as f:
            for i in yaml.safe_load(f) or []:
                knowledge_dict[i["name"]] = i
