import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BOOKS_FOLDER = os.path.join(BASE_DIR, "libros")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=350,
    chunk_overlap=80,
    length_function=len
)

def load_documents(weaviate_service):

    if not os.path.exists(BOOKS_FOLDER):
        raise Exception(f"Folder '{BOOKS_FOLDER}' does not exist")

    files = [
        f for f in os.listdir(BOOKS_FOLDER)
        if f.lower().endswith(".txt")
    ]

    if not files:
        raise Exception("No TXT files were found")


    existing = weaviate_service.get_sources()

    new_files = [f for f in files if f not in existing]
    skipped = [f for f in files if f in existing]

    if not new_files:
        return {
            "books_loaded": [],
            "books_skipped": skipped
        }

    documents = []

    for filename in new_files:
        path = os.path.join(BOOKS_FOLDER, filename)
        loader = TextLoader(path, encoding="utf-8")
        docs = loader.load()

        for doc in docs:
            doc.metadata["source"] = filename

        documents.extend(docs)

    chunks = text_splitter.split_documents(documents)
    inserted = weaviate_service.add_documents(chunks)

    return {
        "books_loaded": new_files,
        "books_skipped": skipped,
        "chunks_created": len(chunks),
        "chunks_inserted": inserted
    }