from fastapi import FastAPI, HTTPException

from models import *
from modulemanager import classregistry, manager

#중요 class 데코레이터 등록을 위해서 필요
import VectorDB.customdbmodule.customdbmodule as customdbmodule
import VectorDB.chromadbmodule.chromadbmodule as chromadbmodule
import VectorDB.milvusdbmodule.milvusdbmodule as milvusdbmodule

app = FastAPI()

@app.post("/{vectordbname}/load")
async def load(file:File, vectordbname: VectorEnum, collection: CollectionEnum = None):
    print(vectordbname.value, file.filename)
    vectordbclass = classregistry.get(vectordbname.value)
    if vectordbclass:
        retrieved_instance = manager.get_module(vectordbname.value)
        if retrieved_instance:
            print("The vectordb you requested has already been loaded.")
            return {'content': "The vectordb you requested has already been loaded." }        
        else: 
            instance = vectordbclass(vectordbname.value)
            result = instance.load(file, collection)
            manager.register_module(instance)
            return result
    else:
        return {'content': "The vectordb you requested is not exist." }    

# @app.post("/{vectordbname}/query")
# async def query(vectordbname:str, query: Query):
#     print(vectordbname)
#     retrieved_instance = manager.get_module(vectordbname)
#     if retrieved_instance:
#         answer = retrieved_instance.query(query)
#         return {'content': answer }
#     else:
#         print("{vectordbname} not found....")
#         return {'content': "{vectordbname}not found...." }

@app.post("/{vectordbname}/query")
async def query(vectordbname:VectorEnum, query: Query, collection: CollectionEnum=None):
    print(vectordbname.value)
    vectordbclass = classregistry.get(vectordbname.value)
    if vectordbclass:
        instance = vectordbclass(vectordbname.value)
        manager.register_module(instance)
        retrieved_instance = manager.get_module(vectordbname.value)
        if retrieved_instance:
            answer = retrieved_instance.query(query, collection)
            return {'content': answer}
        else:
            print(f"{vectordbname.value} not found....")
            answer = retrieved_instance.query(query, collection)
            return {'content': answer }
            # return {'content': f"{vectordbname.value} not found...." }
    else:
        return {'content': "The vectordb you requested is not exist." }

@app.delete("/milvus/collections/{collection_name}", summary='Delete Collection')
async def query(collection_name: CollectionEnum):
    print(collection_name.value)
    vectordbclass = classregistry.get('milvusdb')
    instance = vectordbclass('milvusdb')
    manager.register_module(instance)
    retrieved_instance = manager.get_module('milvusdb')
    if not retrieved_instance:
        print(f'Milvus instance Not Found.')
        raise HTTPException(status_code=404, detail=f'Milvus Not Found.')
    result = retrieved_instance.drop_collection(collection_name.value)
    if not result:
        raise HTTPException(status_code=404, detail=f'{collection_name.value} Collection Not Found.')
    return {'content': f'Success! {collection_name.value} Collection Dropped.'}

@app.get("/milvus/collections/{collection_name}/data/{id}", summary='Get Data')
async def query(collection_name: CollectionEnum, id: str):
    print(collection_name.value, id)
    vectordbclass = classregistry.get('milvusdb')
    instance = vectordbclass('milvusdb')
    manager.register_module(instance)
    retrieved_instance = manager.get_module('milvusdb')
    if not retrieved_instance:
        print(f'Milvus instance Not Found.')
        raise HTTPException(status_code=404, detail=f'Milvus Not Found.')
    result = retrieved_instance.get_data(collection_name.value, id)
    if len(result) == 0:
        raise HTTPException(status_code=404, detail=f'id:{id} Not Found.')
    return result

@app.post("/milvus/collections/{collection_name}/data", summary='Create Data')
async def query(collection_name: CollectionEnum, data: Dict[str, Any]):
    print(collection_name.value)
    vectordbclass = classregistry.get('milvusdb')
    instance = vectordbclass('milvusdb')
    manager.register_module(instance)
    retrieved_instance = manager.get_module('milvusdb')
    if not retrieved_instance:
        print(f'Milvus instance Not Found.')
        raise HTTPException(status_code='404', detail=f'Milvus Not Found.')
    result = retrieved_instance.create_data(collection_name.value, data)
    if not result:
        raise HTTPException(status_code='404', detail=f'{collection_name.value} Collection Not Found.')
    return result

@app.put("/milvus/collections/{collection_name}/data/{id}", summary='Update Data')
async def query(collection_name: CollectionEnum, id: str, data: Dict[str, Any]):
    print(collection_name.value, id)
    vectordbclass = classregistry.get('milvusdb')
    instance = vectordbclass('milvusdb')
    manager.register_module(instance)
    retrieved_instance = manager.get_module('milvusdb')
    if not retrieved_instance:
        print(f'Milvus instance Not Found.')
        raise HTTPException(status_code='404', detail=f'Milvus Not Found.')
    result = retrieved_instance.update_data(collection_name.value, id, data)
    if not result:
        raise HTTPException(status_code='404', detail=f'{collection_name.value} Collection Not Found.')
    return result

@app.delete("/milvus/collections/{collection_name}/data/{id}", summary='Delete Data')
async def query(collection_name: CollectionEnum, id: str):
    print(collection_name.value, id)
    vectordbclass = classregistry.get('milvusdb')
    instance = vectordbclass('milvusdb')
    manager.register_module(instance)
    retrieved_instance = manager.get_module('milvusdb')
    if not retrieved_instance:
        print(f'Milvus instance Not Found.')
        raise HTTPException(status_code='404', detail=f'Milvus Not Found.')
    result = retrieved_instance.delete_data(collection_name.value, id)
    if not result:
        raise HTTPException(status_code='404', detail=f'{collection_name.value} Collection Not Found.')
    return result
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)




