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

    knowledge_list = []
    for file in pathlib.Path("./knowledge").glob("**/*.yaml"):
        with open(file, "r", encoding="utf-8") as f:
            knowledge_list.extend(yaml.safe_load(f) or [])
    knowledge_dict = {
        i["name"]: i for i in knowledge_list if i["name"] not in embedding_3_large
    }
    for key in knowledge_dict:
        knowledge = knowledge_dict[key]
        print(f"Processing {key}")
        try:
            embedding_3_large[key] = {
                "content": get_embedding(knowledge["content"]).embedding,
            }
            if "description" in knowledge:
                embedding_3_large[key]["description"] = (
                    get_embedding(knowledge["description"]).embedding,
                )
        except Exception as e:
            print(f"Error processing {key}: {e}")

    with open(
        pathlib.Path(".") / "embedding" / "embedding_3_large.yaml",
        "w",
        encoding="utf-8",
    ) as f:
        yaml.dump(embedding_3_large, f, sort_keys=False, allow_unicode=True)