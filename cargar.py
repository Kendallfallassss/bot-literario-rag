import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Current script folder
BOOKS_FOLDER = os.path.join(BASE_DIR, "libros")  # Folder with book TXT files

# Split text into chunks with overlap for semantic search
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=350,
    chunk_overlap=80,
    length_function=len
)

def load_documents(weaviate_service):
    # Check if folder exists
    if not os.path.exists(BOOKS_FOLDER):
        raise Exception(f"Folder '{BOOKS_FOLDER}' does not exist")

    # List all TXT files
    files = [
        f for f in os.listdir(BOOKS_FOLDER)
        if f.lower().endswith(".txt")
    ]

    if not files:
        raise Exception("No TXT files were found")

    # Check which books already exist in Weaviate
    existing = weaviate_service.get_sources()
    new_files = [f for f in files if f not in existing]  # Books to load
    skipped = [f for f in files if f in existing]        # Books already loaded

    if not new_files:
        return {
            "books_loaded": [],
            "books_skipped": skipped
        }

    documents = []

    # Load new books
    for filename in new_files:
        path = os.path.join(BOOKS_FOLDER, filename)
        loader = TextLoader(path, encoding="utf-8")
        docs = loader.load()  # Read text file

        # Add source metadata
        for doc in docs:
            doc.metadata["source"] = filename

        documents.extend(docs)

    # Split documents into chunks for semantic search
    chunks = text_splitter.split_documents(documents)
    inserted = weaviate_service.add_documents(chunks)  # Add chunks to Weaviate

    # Return summary
    return {
        "books_loaded": new_files,
        "books_skipped": skipped,
        "chunks_created": len(chunks),
        "chunks_inserted": inserted
    }