from fastapi import FastAPI, HTTPException 
from models import *
from module_manager import vectordb_load, vectordb_query

#중요 class 데코레이터 등록을 위해서 필요
import VectorDB.customdb.customdbmodule as customdbmodule
import VectorDB.chromadb.chromadbmodule as chromadbmodule
import VectorDB.milvusdb.milvusdbmodule as milvusdbmodule

from typing import List

from typing import List

app = FastAPI()

@app.post("/{vectordbname}/load")

async def load(vectordbname: str, file:File):
    return vectordb_load(vectordbname, file)



@app.post("/{vectordbname}/query")
async def query(vectordbname:str, query: Query):
    return vectordb_query(vectordbname, query)


@app.post("/milvus/collections", summary='Create Collection')
async def query(collection_name: str, fieldSchema: List[FieldSchema]):
    print(collection_name)

@app.delete("/milvus/collections/{collection_name}", summary='Delete Collection')
async def query(collection_name: CollectionEnum):
    print(collection_name.value)
    retrieved_instance = manager.get_module('milvusdb')
    if not retrieved_instance:
        print(f'Milvus instance Not Found.')
        raise HTTPException(status_code='404', detail=f'Milvus Not Found.')
    result = retrieved_instance.drop_collection(collection_name.value)
    if not result:
        raise HTTPException(status_code='404', detail=f'{collection_name.value} Collection Not Found.')
    return {'content': f'Success! {collection_name.value} Collection Dropped.'}

@app.get("/milvus/collections/{collection_name}/data", summary='List Data')
async def query(collection_name: CollectionEnum, offset: int=0, limit: int=5):
    print(collection_name.value)

@app.post("/milvus/collections/{collection_name}/data", summary='Create Data')
async def query(collection_name: CollectionEnum, data: Data):
    print(collection_name.value)

@app.get("/milvus/collections/{collection_name}/data/{id}", summary='Get Data')
async def query(collection_name: CollectionEnum, id: str):
    print(collection_name.value)


@app.put("/milvus/collections/{collection_name}/data/{id}", summary='Update Data')
async def query(collection_name: CollectionEnum, id: str, data: Data):
    print(collection_name.value)

@app.delete("/milvus/collections/{collection_name}/data/{id}", summary='Delete Data')
async def query(collection_name: CollectionEnum, id: str):
    print(collection_name.value, id)
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)




