import os, json, uuid
from tqdm import tqdm
from openai import OpenAI
from pymilvus import *
from fastapi import HTTPException

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
# HOST = '129.254.177.85'
PORT = 19530

class Milvus:
    def __init__(self):
        self.leeetcode_fields = ["id", "title", "topic", "languages", "level", "description", "examples", "constraints", "testcases", "code_template"]
        self.robotics_fields = ["description"]
        self.humaneval_fields = ["id", "prompt", "entry_point", "canonical_solution", "test"]
        self.suresoft__fields = ["id", "TpTitle", "TpName", "ruleTitle", "ruleName", "ruleDescription", "example_name", "example_code", "checker_header_name", "checker_header_code", "checker_implementation_name", "checker_implementation_code"]
        pass
    
    def connect_collection(self, collection_name):
        print(f"<Collection>:\n -------------\n <Host:Port> {HOST}:{PORT}")
        connections.connect(host=HOST, port=PORT)
        try:
            collection = Collection(f"{collection_name}")      # Get an existing collection.
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
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
    def delete(self, collection, id):
        collection.delete(f'id == {id}')
    
    def scalar_query(self, collection, expr, limit=1):
        output_fields = None
        if collection.name == 'leetcode':
            output_fields = self.leeetcode_fields
        if collection.name == 'robotics':
            output_fields = self.robotics_fields
        if collection.name == 'humaneval':
            output_fields = self.humaneval_fields
        if collection.name == 'suresoft':
            output_fields = self.suresoft__fields

        result = collection.query(
            expr= expr,
            output_fields= output_fields,
            limit = limit
        )
        
        return result
    
    def search(self, collection, query, top_k):
        anns_field = 'embedding'
        output_fields = None
        if collection.name == 'leetcode':
            output_fields = self.leeetcode_fields
        if collection.name == 'robotics':
            output_fields = self.robotics_fields
        if collection.name == 'humaneval':
            output_fields = self.humaneval_fields
        if collection.name == 'suresoft':
            output_fields = self.suresoft__fields

        outputs = collection.search(
            data=[self.embed(query)], 
            anns_field=anns_field, 
            param=QUERY_PARAM,
            limit=top_k,
            output_fields = output_fields
        )
        response = []
        for output in outputs:
            for record in output:
                tmp = {
                    "id": record.id,
                    "distance": record.distance,
                    "entity": {}
                }
                if output_fields != None:
                    for field in output_fields:
                        tmp["entity"].update({
                            f"{field}": record.get(field)
                        })
                response.append(tmp)
        for item in response:
            for key in item['entity']:
                value = item['entity'][key]
                if type(value).__name__ == 'RepeatedScalarContainer':
                    item['entity'][key] = list(value)
            
        result = sorted(response, key=lambda x: x['distance'])
        print(outputs)
        return result


class DataProcess:
    def __init__(self) -> None:
        pass

    def insert_grepp(self, json_data):
        grepp_fields = [
            FieldSchema(name='id', dtype=DataType.INT64, is_primary=True),
            FieldSchema(name='title', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='partTitle', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='languages', dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=900, max_length=1000),
            FieldSchema(name='level', dtype=DataType.INT16),
            FieldSchema(name='description', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='testcases', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
        ]
        milvus = Milvus()
        collection = milvus.create_collection(collection_name='grepp', fields=grepp_fields, embed_field='embedding')
        collection = milvus.connect_collection(collection_name='grepp')
        print(f"===== Start Inserting data to '{collection.name}' ===== ")
        for element in tqdm(json_data):
            data = [{
                'id': element['id'],
                'title': element['title'],
                'partTitle': element['partTitle'],
                'languages': element['languages'],
                'level': element['level'],
                'description': element['description'], 
                'testcases': str(element['testcases']),
                'embedding': milvus.embed(
                    element['title'] + element['partTitle'] + element['description'] + str(element['testcases'])
                )
            }]
            print(f"------------- Upserting {element['id']} -------------")
            milvus.upsert(collection=collection, data=data)

        print(f"===== End Inserting data to '{collection.name}' ===== ")
    
    def insert_leetcode(self, json_data):
        leetcode_fields = [
            FieldSchema(name='id', dtype=DataType.INT64, is_primary=True),
            FieldSchema(name='title', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='topic', dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=900, max_length=1000),
            FieldSchema(name='languages', dtype=DataType.ARRAY, element_type=DataType.VARCHAR, max_capacity=900, max_length=1000),
            FieldSchema(name='level', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='description', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='examples', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='constraints', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='testcases', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='code_template', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=DIMENSION),
        ]
        milvus = Milvus()
        collection = milvus.create_collection(collection_name='leetcode', fields=leetcode_fields, embed_field='embedding')
        collection = milvus.connect_collection(collection_name='leetcode')
        print(f"===== Start Inserting data to '{collection.name}' ===== ")
        for element in tqdm(json_data):
            topics_sum = ''
            for topic in element['topic']:
                topics_sum = topics_sum + topic
            data = [{
                'id': element['problem_id'],
                'title': element['title'],
                'topic': element['topic'],
                'languages': element['languages'],
                'level': element['level'],
                'description': element['description'], 
                'examples': element['examples'],
                'constraints': element['constraints'],
                'testcases': element['testcases'],
                'code_template': element['code_template'],
                'embedding': milvus.embed(
                    element['title'] + topics_sum + element['description'] + element['examples'] + element['constraints'] + element['code_template']
                )
            }]
            print(f"------------- Upserting {element['problem_id']} -------------")
            milvus.upsert(collection=collection, data=data)

        print(f"===== End Inserting data to '{collection.name}' ===== ")
    
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
        suresoft_fields = [
            FieldSchema(name='id', dtype=DataType.VARCHAR, max_length=64, is_primary=True),
            FieldSchema(name='TpTitle', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='TpName', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='ruleTitle', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='ruleName', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='ruleDescription', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='example_name', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='example_code', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='checker_header_name', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='checker_header_code', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='checker_implementation_name', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='checker_implementation_code', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='embedding', 
                        dtype=DataType.FLOAT_VECTOR, 
                        dim=DIMENSION, 
                        description="TpTitle + TpName + ruleTitle + ruleName + ruleDescription + example_code + checker_header_code + checker_implementation_code"),
        ]
        milvus = Milvus()
        collection = milvus.create_collection(collection_name='suresoft', fields=suresoft_fields, embed_field='embedding')
        collection = milvus.connect_collection(collection_name='suresoft')
        
        print(f"------------- Start to '{collection.name}' ------------- ")
        for element in tqdm(json_data):
            data = [{
                'id': element['id'],
                'TpTitle': element['TpTitle'],
                'TpName': element['TpName'],
                'ruleTitle': element['ruleTitle'],
                'ruleName': element['ruleName'],
                'ruleDescription': element['ruleDescription'],
                'example_name': element['example']['name'],
                'example_code': element['example']['code'],
                'checker_header_name': element['checker_header']['name'],
                'checker_header_code': element['checker_header']['code'],
                'checker_implementation_name': element['checker_implementation']['name'],
                'checker_implementation_code': element['checker_implementation']['code'],
                'embedding': milvus.embed(
                    element['TpTitle'] +\
                    element['TpName'] +\
                    element['ruleTitle'] +\
                    element['ruleName'] +\
                    element['ruleDescription'] +\
                    element['example']['code'] +\
                    element['checker_header']['code'] +\
                    element['checker_implementation']['code']
                )
            }]
            print(f"------------- Upserting {element['id']} -------------")
            try:
                milvus.upsert(collection = collection, data = data)
            except Exception as e:
                print(e)
        print(f"------------- End to '{collection.name}' -------------")

    def insert_humaneval(self, json_data):
        humaneval_fields = [
            FieldSchema(name='id', dtype=DataType.INT64, is_primary=True),
            FieldSchema(name='task_id', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='prompt', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='entry_point', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='canonical_solution', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='test', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=DIMENSION, description="prompt & canonical_solution"),
        ]
        milvus = Milvus()
        collection = milvus.create_collection(collection_name='humaneval', fields=humaneval_fields, embed_field='embedding')
        collection = milvus.connect_collection(collection_name='humaneval')
        
        print(f"------------- Start to '{collection.name}' ------------- ")
        for element in tqdm(json_data):
            data = [{
                'id': int(element['task_id'].split('/')[1]),
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
        solution_fields = [
            FieldSchema(name='id', dtype=DataType.VARCHAR, max_length=640, is_primary=True),
            FieldSchema(name='source', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='solution_id', dtype=DataType.INT64),
            FieldSchema(name='problem_id', dtype=DataType.INT64),
            FieldSchema(name='language', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='code', dtype=DataType.VARCHAR, max_length=64000),
            FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=DIMENSION, description="language & code"),
        ]
        milvus = Milvus()
        collection = milvus.create_collection(collection_name='solution', fields=solution_fields, embed_field='embedding')
        collection = milvus.connect_collection(collection_name='solution')
        
        print(f"------------- Start to '{collection.name}' ------------- ")
        for element in tqdm(json_data):
            id = f"{element['source']}-{element['solution_id']}-{element['problem_id']}"
            data = [{
                'id': id,
                'source': element['source'],
                'solution_id': element['solution_id'],
                'problem_id': element['problem_id'],
                'language': element['language'],
                'code': element['code'],
                'embedding': milvus.embed(element['language']+element['code'])
            }]
            print(f"------------- Upserting {id} -------------")
            milvus.upsert(collection = collection, data = data)
        print(f"------------- End to '{collection.name}' -------------")

