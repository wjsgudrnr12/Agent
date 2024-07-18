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
        expr = f"id == {id}"
        
        result = self.milvus.scalar_query(collection=coll, expr=expr)
        return result

    def update_data(self, collection_name, id, data):
        collection = self.milvus.connect_collection(collection_name)
        expr = f"id == {id}"
        
        result = self.milvus.scalar_query(collection=collection, expr=expr)
        if len(result) == 0:
            raise HTTPException(status_code=404, detail=f'id:{id} Not Found.')
        try:
            print(result)
            self.milvus.upsert(collection=collection, data=data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"{e}")
        return result
    
    def create_data(self, collection_name, data):
        collection = self.milvus.connect_collection(collection_name)
        expr = f"id == {data.id}"
        
        result = self.milvus.scalar_query(collection=collection, expr=expr)
        if not len(result) == 0:
            raise HTTPException(status_code=404, detail=f'id:{id} Found.')
        try:
            print(result)
            self.milvus.ingest(collection=collection, data=data)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"{e}")
        return result

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
    