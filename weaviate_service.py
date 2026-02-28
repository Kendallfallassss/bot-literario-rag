from urllib import response

import weaviate
import weaviate.classes as wvc
from weaviate.classes.query import MetadataQuery
from langchain_community.embeddings import OllamaEmbeddings


class WeaviateService:

    def __init__(self):
        self.client = weaviate.connect_to_local()
        self.embeddings = OllamaEmbeddings(model="nomic-embed-text")
        self._init_collection()

    def _init_collection(self):
        collections = self.client.collections.list_all()
        if "BookChunk" not in collections:
            self.client.collections.create(
                name="BookChunk",
                vectorizer_config=wvc.config.Configure.Vectorizer.none(),
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
        self.collection = self.client.collections.get("BookChunk")

    def clear(self):
        self.client.collections.delete("BookChunk")
        self._init_collection()

    def add_documents(self, chunks):
        with self.collection.batch.dynamic() as batch:
            for chunk in chunks:
                vector = self.embeddings.embed_query(chunk.page_content)
                batch.add_object(
                    properties={
                        "text": chunk.page_content,
                        "source": chunk.metadata.get("source", "unknown")
                    },
                    vector=vector
                )
        return len(chunks)

    def search(self, query, limit=20):
        query_vector = self.embeddings.embed_query(query)

        response = self.collection.query.near_vector(
            near_vector=query_vector,
            limit=limit,
            return_metadata=MetadataQuery(distance=True)
        )

        for obj in response.objects:
            print("DIST:", obj.metadata.distance)

        return [
            obj.properties["text"]
            for obj in response.objects
            if obj.properties.get("text")
        ]
    
    def get_sources(self):
        res = self.collection.query.fetch_objects(limit=1000)
        return {
        obj.properties["source"]
        for obj in res.objects
        if "source" in obj.properties
        }
    