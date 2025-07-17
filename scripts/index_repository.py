from qdrant_client import QdrantClient, models
import os
import glob

def generate_embeddings(file_content: str) -> list[float]:
    # Placeholder for embedding generation logic
    # Replace with actual embedding model call
    return [0.0] * 768  # Example fixed-size vector

def index_codebase():
    qdrant_url = os.getenv("QDRANT_URL")
    mem0_token = os.getenv("MEM0_TOKEN")

    qdrant = QdrantClient(url=qdrant_url)
    # Mem0 client import and usage commented out due to unresolved import
    # mem0 = MemoryClient(token=mem0_token)

    # Recursively find code files in the repository
    code_files = glob.glob("**/*.py", recursive=True) + glob.glob("**/*.ts", recursive=True) + glob.glob("**/*.tsx", recursive=True) + glob.glob("**/*.js", recursive=True)

    for file_path in code_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        embeddings = generate_embeddings(content)

        # Upsert to Qdrant vector store using PointStruct model
        point = models.PointStruct(
            id=file_path,
            vector=embeddings,
            payload={"path": file_path, "content": content[:1000]}  # Store snippet for quick preview
        )
        qdrant.upsert(
            collection_name="codebase",
            points=[point]
        )

        # Store context in Mem0 - commented out until import resolved
        # mem0.store_context(file_path, content)

if __name__ == "__main__":
    index_codebase()
