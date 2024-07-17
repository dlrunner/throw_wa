from pinecone import Pinecone, ServerlessSpec
from pinecone.exceptions import PineconeException
from datetime import datetime, timedelta
from collections import Counter

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
            if 'date' in metadata:
                metadata['date'] = metadata["date"].split('T')[0]
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
        
    def search_by_metadata(self, metadata):
        try:
            self.create_index_if_not_exists()
            # zero vector의 차원을 인덱스의 차원과 일치시키기
            zero_vector = [0.0] * self.dimension
            response = self.index.query(
                vector=zero_vector,
                top_k=10,
                include_metadata=True,
                filter=metadata
            )
            return response
        except PineconeException as e:
            raise ValueError(f"Failed to search by metadata: {str(e)}")
        
    def query_by_metadata(self, metadata_filter: dict):
        try:
            self.create_index_if_not_exists()
            zero_vector = [0.0] * self.dimension
            response = self.index.query(
                vector=zero_vector,
                top_k=10,
                include_metadata=True,
                filter=metadata_filter
            )
            return response
        except PineconeException as e:
            raise ValueError(f"Failed to query vector: {str(e)}")
        
    def get_keyword_rankings(self):
        try:
            response = self.query_by_metadata({})
            if not response or not response['matches']:
                return None
            
            keyword_counter = Counter()
            for match in response['matches']:
                keyword = match['metadata'].get('keyword')
                if keyword:
                    keyword_counter[keyword] += 1

            sorted_keywords = keyword_counter.most_common()
            return sorted_keywords
        except Exception as e :
            raise ValueError(f"키워드 별 랭킹 실패: {str(e)}")
        
    def get_top_n_by_type(self, n: int = 5):
        try:
            self.create_index_if_not_exists()
            zero_vector = [0.0] * self.dimension
            response = self.index.query(
                vector=zero_vector,
                top_k=1000,  # 임의의 큰 값으로 설정
                include_metadata=True,
                filter={}
            )
            if not response or not response['matches']:
                return None
            
            type_dict = {}
            for match in response['matches']:
                type_ = match['metadata'].get('type')
                if type_ not in type_dict:
                    type_dict[type_] = []
                if len(type_dict[type_]) < n:
                    type_dict[type_].append(match['metadata'])
            
            return type_dict
        except PineconeException as e:
            raise ValueError(f"Failed to get top N by type: {str(e)}")