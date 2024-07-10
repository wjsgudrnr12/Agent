import os, json
from tqdm import tqdm
from openai import OpenAI
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
EMBED_MODEL = 'text-embedding-ada-002'
HOST = '127.0.0.1'
PORT = 19530

class Milvus:
    def __init__(self):
        pass
    
    def connect_collection(self, collection_name):
        print(f"<Collection>:\n -------------\n <Host:Port> {HOST}:{PORT}")
        connections.connect(host=HOST, port=PORT)
        collection = Collection(f"{collection_name}")      # Get an existing collection.
        collection.load()
        return collection
    
    def create_collection(self, collection_name, fields, embed_field):
        connections.connect(host=HOST, port=PORT)
        print(f"<Database>:\n -------------\n <Host:Port> {HOST}:{PORT}")
        print(f' <Name>{collection_name}')
        
        if utility.has_collection(f'{collection_name}'):
            utility.drop_collection(f'{collection_name}')
        
        schema = CollectionSchema(fields=fields, enable_dynamic_field=True)
        collection = Collection(name=f'{collection_name}', schema=schema)
        collection.create_index(field_name=f"{embed_field}", index_params=INDEX_PARAM)
        collection.load()
        return collection

    def embed(self, text):
        openAIclient = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        response = openAIclient.embeddings.create(
            input=text,
            model='text-embedding-3-small'
        )
        return response.data[0].embedding
    
    def ingest(self, collection, data):
        collection.insert([{'description':element, 'embedding': self.embed(element)} for element in tqdm(data)])
    
    def search(self, collection, query, top_k):
        if collection.name == 'robotics':
            output_fields = ["description"]
        outputs = collection.search(
            data=[self.embed(query)], 
            anns_field='embedding', 
            param=QUERY_PARAM,
            limit=top_k,
            output_fields = output_fields
        )
        print(outputs)
        response = []
        for output in outputs:
            for record in output:
                tmp = {
                    "id": record.id,
                    "distance": record.distance,
                    "entity": {}
                }
                for field in output_fields:
                    tmp["entity"].update({
                        f"{field}": record.get(field)
                    })
                response.append(tmp)
        result = {
            "request": {
                "collection": collection.name,
                "anns_field": 'embedding',
                "param": QUERY_PARAM,
                "limit": top_k,
            },
            "response": sorted(response, key=lambda x: x['distance'])
            # "response": json.dumps(outputs, indent=4)
        }
        return result


class DataProcess:
    def __init__(self) -> None:
        pass

    def insert_grepp(self, json_data):
        print(json_data)
    
    def insert_leetcode(self, json_data):
        print(json_data)
    
    def insert_robotics(self, json_data):
        robotics_fields = [
            FieldSchema(name='id', dtype=DataType.INT64, is_primary=True, auto_id=True),
            FieldSchema(name='description', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
        ]
        milvus = Milvus()
        collection = milvus.create_collection(collection_name='robotics', fields=robotics_fields, embed_field='embedding')
        collection = milvus.connect_collection(collection_name='robotics')
        array = []
        for element in json_data:
            array.append(element['content'])
        print(f"===== Start Inserting data to '{collection.name}' ===== ")
        milvus.ingest(collection=collection, data=array)
        print(f"===== End Inserting data to '{collection.name}' ===== ")
    
    def insert_suresoft(self, json_data):
        print(json_data)

    def insert_solutions(self, json_data):
        print(json_data)

