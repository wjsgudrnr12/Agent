from fastapi import FastAPI, Depends

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
            return {'content': answer }
        else:
            print(f"{vectordbname.value} not found....")
            answer = retrieved_instance.query(query, collection)
            return {'content': answer }
            # return {'content': f"{vectordbname.value} not found...." }
    else:
        return {'content': "The vectordb you requested is not exist." }

@app.get("/milvusdb/problem/{id}")
async def query(problem_id: str):
    return 

@app.get("/milvusdb/solution/{id}")
async def query(solution: Solution):
    return 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)




