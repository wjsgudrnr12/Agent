import json
from tqdm import tqdm
from fastapi import FastAPI, HTTPException
from VectorDB.milvusdbmodule.milvus import Milvus, DataProcess
from models import Document, File, Query
from modulemanager import classregistry

@classregistry.register('milvusdb', )
class MilvusdbModule:
    def __init__(self, name):
        self.name = name
        self.milvus = Milvus()
        self.dataProcess = DataProcess()
        self.suresoft_embed_fields = ["TpTitle", "TpName", "ruleTitle", "ruleName", "ruleDescription", "example_code", "checker_header_code", "checker_implementation_code"]
        pass

    def some_method(self):
        pass

    def load(self, file: File, collection):
        filename = file.filename
        try:
            content = file.file.read()
            data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        print(collection.value)
        if collection.value == 'grepp':
            self.dataProcess.insert_grepp(data)
        if collection.value == 'leetcode':
            self.dataProcess.insert_leetcode(data)
        if collection.value == 'robotics':
            self.dataProcess.insert_robotics(data)
        if collection.value == 'suresoft':
            self.dataProcess.insert_suresoft(data)
        if collection.value == 'humaneval':
            self.dataProcess.insert_humaneval(data)
        if collection.value == 'solutions':
            self.dataProcess.insert_solutions(data)

        return {
            "filename": filename
        }
    
    def query(self, query, collection):
        print(collection.value)
        coll = self.milvus.connect_collection(collection.value)
        result = self.milvus.search(coll, query.query, query.top_k)

        return result
    
    def get_data(self, collection_name, id):
        coll = self.milvus.connect_collection(collection_name)
        if collection_name == 'suresoft':
            expr = f"id == '{id}'"
        else:
            expr = f"id == {id}"

        result = self.milvus.scalar_query(collection=coll, expr=expr)
        return result

    def create_data(self, collection_name, data):
        collection = self.milvus.connect_collection(collection_name)
        if collection_name == 'suresoft':
            expr = f'id == "{data["id"]}"'
        else:
            expr = f'id == {data["id"]}'
        
        found = self.milvus.scalar_query(collection=collection, expr=expr)
        if found:
            raise HTTPException(status_code=409, detail=f'{found["id"]} Already Exists.')
        try:
            if collection_name == 'suresoft':
                data['embedding'] = self.milvus.embed(
                    "".join(data[key] for key in self.suresoft_embed_fields if key in data)
                )
            self.milvus.ingest(collection=collection, data=data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"{e}")
        return {"id": data["id"]}

    def update_data(self, collection_name, id, data):
        try:
            collection = self.milvus.connect_collection(collection_name)
        except Exception as e:
            raise HTTPException(status_code=500, detail=e)
        if collection_name == 'suresoft':
            expr = f"id == '{id}'"
        else:
            expr = f"id == {id}"
        
        found = self.milvus.scalar_query(collection=collection, expr=expr)
        if len(found) == 0:
            raise HTTPException(status_code=404, detail=f'id:{id} Not Found.')
        try:
            for key in data:
                if key in found[0]:
                    found[0][key] = data[key]
            if collection_name == 'suresoft':
                found[0]['embedding'] = self.milvus.embed(
                    "".join(found[key] for key in self.suresoft_embed_fields if key in found)
                )
            self.milvus.upsert(collection=collection, data=found)
        except Exception as e:
            raise HTTPException(status_code=400, detail=e)
        return {"result": f"id:{id} Updated."}   

    def delete_data(self, collection_name, id):
        collection = self.milvus.connect_collection(collection_name)
        expr = f"id == {id}"
        
        result = self.milvus.scalar_query(collection=collection, expr=expr)
        if len(result) == 0:
            raise HTTPException(status_code=404, detail=f'id:{id} Not Found.')
        try:
            print(result)
            self.milvus.delete(collection=collection, id=id)
            return {"result": f"id:{id} Deleted."}
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"{e}")
    
    def drop_collection(self, collection_name):
        self.milvus.connect_collection(collection_name)
        result = self.milvus.drop(collection_name)
        
        return result
    