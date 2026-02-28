from urllib import response

import weaviate
import weaviate.classes as wvc
from weaviate.classes.query import MetadataQuery
from langchain_community.embeddings import OllamaEmbeddings


class WeaviateService:

    def __init__(self):
        self.client = weaviate.connect_to_local()  # Connect to local Weaviate instance
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")  # Embedding model
        self._init_collection()  # Initialize collection

    def _init_collection(self):
        collections = self.client.collections.list_all()  # List all collections
        if "BookChunk" not in collections:
            # Create collection if it doesn't exist
            self.client.collections.create(
                name="BookChunk",
                vectorizer_config=wvc.config.Configure.Vectorizer.none(),  # No built-in vectorizer
                properties=[
                    wvc.config.Property(
                        name="text",
                        data_type=wvc.config.DataType.TEXT
                    ),
                    wvc.config.Property(
                        name="source",
                        data_type=wvc.config.DataType.TEXT
                    )
                ]
            )
        self.collection = self.client.collections.get("BookChunk")  # Get the collection

    def clear(self):
        self.client.collections.delete("BookChunk")  # Delete collection
        self._init_collection()  # Recreate empty collection

    def add_documents(self, chunks):
        # Add multiple chunks/documents in batch
        with self.collection.batch.dynamic() as batch:
            for chunk in chunks:
                vector = self.embeddings.embed_query(chunk.page_content)  # Generate vector
                batch.add_object(
                    properties={
                        "text": chunk.page_content,
                        "source": chunk.metadata.get("source", "unknown")
                    },
                    vector=vector
                )
        return len(chunks)  # Return number of added chunks

    def search(self, query, limit=20):
        query_vector = self.embeddings.embed_query(query)  # Embed the query

        response = self.collection.query.near_vector(
            near_vector=query_vector,
            limit=limit,
            return_metadata=MetadataQuery(distance=True)  # Include distance info
        )

        for obj in response.objects:
            print("DIST:", obj.metadata.distance)  # Debug: print distance of each object

        # Return list of texts found
        return [
            obj.properties["text"]
            for obj in response.objects
            if obj.properties.get("text")
        ]
    
    def get_sources(self):
        # Get all unique book sources from the collection
        res = self.collection.query.fetch_objects(limit=1000)
        return {
            obj.properties["source"]
            for obj in res.objects
            if "source" in obj.properties
        }