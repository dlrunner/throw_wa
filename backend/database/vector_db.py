from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeException

class VectorDatabase:
    def __init__(self, api_key: str, environment: str, index_name: str, dimension: int):
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.dimension = dimension
        self.pc = None
        self.index = None
    
    def init_pinecone(self):
        self.pc = Pinecone(api_key=self.api_key, environment=self.environment)
    
    def create_index_if_not_exists(self):
        if not self.index:
            if not self.pc:
                self.init_pinecone()
            
            if self.index_name not in self.pc.list_indexes().names():
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine"
                )
            self.index = self.pc.Index(self.index_name)
    
    def upsert_vector(self, vector_id: str, vector: list, metadata: dict):
        try:
            self.create_index_if_not_exists()
            self.index.upsert(
                vectors=[{
                    "id": vector_id,
                    "values": vector,
                    "metadata": metadata
            }]
        )
        except PineconeException as e:
            raise ValueError(f"Failed to upsert vector: {str(e)}")

    def query_vector(self, query_vector: list, top_k: int, metadata_filter: dict):
        try:
            self.create_index_if_not_exists()
            response = self.index.query(
                vector=query_vector,
                top_k=top_k,
                include_values=True,
                include_metadata=True,
                filter=metadata_filter
            )
            return response
        except PineconeException as e:
            raise ValueError(f"Failed to query vector: {str(e)}")
