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
    print(vectordbname, file.filename)
    vectordbclass = classregistry.get(vectordbname)
    if vectordbclass:
        retrieved_instance = manager.get_module(vectordbname)
        if retrieved_instance:
            print("The vectordb you requested has already been loaded.")
            return {'content': "The vectordb you requested has already been loaded." }        
        else: 
            instance = vectordbclass(vectordbname)
            result = instance.load(file, collection)
            manager.register_module(instance)
            return result
    else:
        return {'content': "The vectordb you requested is not exist." }    

@app.post("/{vectordbname}/query")
async def query(vectordbname:str, query: Query):
    print(vectordbname)
    retrieved_instance = manager.get_module(vectordbname)
    if retrieved_instance:
        answer = retrieved_instance.query(query)
        return {'content': answer }
    else:
        print("{vectordbname} not found....")
        return {'content': "{vectordbname}not found...." }

@app.get("/milvusdb/problem/{id}")
async def query(problem_id: str):
    return 

@app.get("/milvusdb/solution/{id}")
async def query(solution: Solution):
    return 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)




