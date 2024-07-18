import os
from pymilvus import *

DIMENSION = 1536
INDEX_PARAM = {
    'metric_type':'L2',
    'index_type':"HNSW",
    'params':{'M': 8, 'efConstruction': 64}
}
QUERY_PARAM = {
    "metric_type": "L2",
    "params": {"ef": 64},
}

class Milvus:
    def __init__(self, collection_name):
        if not os.path.exists("./milvusdb"):
            os.makedirs("./milvusdb")
        self.client = MilvusClient(f"./milvusdb/milvus.db")
        connections.connect("default", uri=f"./milvusdb/milvus.db")
        if utility.has_collection(f'{collection_name}'):
            self.collection = Collection(f"{collection_name}")
        else:
            fields = [
                #...
            ]
            schema = CollectionSchema(fields=fields)
            collection = Collection(name=f'{collection_name}', schema=schema)
            collection.create_index(field_name="embedding", index_params=INDEX_PARAM)
        
        self.collection.load()
    
    def method(self, ):
        print()
        