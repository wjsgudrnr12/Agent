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
            # utility.drop_collection(f'{collection_name}')
            print(f' <Name>{collection_name} Already Exists -------------')
            return
        else:
            schema = CollectionSchema(fields=fields, enable_dynamic_field=True)
            collection = Collection(name=f'{collection_name}', schema=schema)
            if type(embed_field) == list:
                for i in range(len(embed_field)):
                    collection.create_index(field_name=f"{embed_field[i]}", index_params=INDEX_PARAM)
            else:
                collection.create_index(field_name=f"{embed_field}", index_params=INDEX_PARAM)
            print(f' <Name>{collection_name} Created -------------')
            collection.load()
            return collection
        
    def drop(self, collection_name):
        if utility.has_collection(f'{collection_name}'):
            print(f' <Name>{collection_name} Exists -------------')
            utility.drop_collection(f'{collection_name}')
            return True
        else:
            print(f' <Name>{collection_name} Not Found -------------')
            return False

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
        collection.insert(data)
    def upsert(self, collection, data):
        collection.upsert(data)
    
    def scalar_query(self, collection, expr):
        if collection.name == 'robotics':
            output_fields = ["description"]
        if collection.name == 'humaneval':
            output_fields = ["task_id", "prompt", "entry_point", "canonical_solution", "test"]
        result = collection.query(
            expr= expr,
            output_fields= output_fields
        )
        return result
    
    def search(self, collection, query, top_k):
        if collection.name == 'robotics':
            anns_field = 'embedding'
            output_fields = ["description"]
        if collection.name == 'humaneval':
            anns_field = 'embedding'
            output_fields = ["task_id", "prompt", "entry_point", "canonical_solution", "test"]
        outputs = collection.search(
            data=[self.embed(query)], 
            anns_field=anns_field, 
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
                "anns_field": anns_field,
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
        # array = []
        # for element in json_data:
        #     array.append(element['content'])
        print(f"===== Start Inserting data to '{collection.name}' ===== ")
        for element in tqdm(json_data):
            milvus.ingest(collection=collection, data=[{'description':element['content'], 'embedding': milvus.embed(element['content'])}])

        print(f"===== End Inserting data to '{collection.name}' ===== ")
    
    def insert_suresoft(self, json_data):
        print(json_data)

    def insert_humaneval(self, json_data):
        humaneval_fields = [
            FieldSchema(name='task_id', dtype=DataType.VARCHAR, max_length=64000, is_primary=True, auto_id=False),
            FieldSchema(name='prompt', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='entry_point', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='canonical_solution', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='test', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
        ]
        milvus = Milvus()
        collection = milvus.create_collection(collection_name='humaneval', fields=humaneval_fields, embed_field=['prompt_embedding', 'solution_embedding', 'prompt_solution_embedding'])
        collection = milvus.connect_collection(collection_name='humaneval')
        
        print(f"------------- Start to '{collection.name}' ------------- ")
        for element in tqdm(json_data):
            data = [{
                'task_id':element['task_id'],
                'prompt':element['prompt'],
                'entry_point':element['entry_point'],
                'canonical_solution':element['canonical_solution'],
                'test':element['test'],
                'embedding': milvus.embed(element['prompt']+element['canonical_solution'])
            }]
            print(f"------------- Upserting {element['task_id']} -------------")
            milvus.upsert(collection = collection, data = data)
        print(f"------------- End to '{collection.name}' -------------")

    def insert_solutions(self, json_data):
        print(json_data)

