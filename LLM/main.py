from fastapi import FastAPI
import locale
import uvicorn

from models import *
from modulemanager import classregistry, manager

#중요 class 데코레이터 등록을 위해서 필요
from LLM.koalpacamodule.interence_koalpaca_12_8 import Koalpach_12_8_LLMModel

locale.getpreferredencoding = lambda: "UTF-8"

app = FastAPI()
#llmmodel = Koalpach_12_8_LLMModel()

@app.get('/')
async def chat():
    return 'Hello World!'

@app.get('/{modelname}/load')
async def load(modelname:str) -> Answer:
    print(modelname)
    llmclass = classregistry.get(modelname)
    if llmclass:
        
        retrieved_instance = manager.get_module(modelname)
        if retrieved_instance is not None:
            print("The model you requested has already been loaded.")
            return {'content': "The model you requested has already been loaded." }        
        
        else:    
            instance = llmclass(modelname)
            instance.modelinit()
            manager.register_module(instance)
            #answer = instance.gen("1980년대에 첫 번째 혁신적인 기술을 보셨다고 하셨는데, 어떤 기술이었나요?")
            return {'content': "model load ok" }


@app.post('/{modelname}/query')
async def query(modelname:str, prompt: Prompt) -> Answer:
    print(modelname)
    retrieved_instance = manager.get_module(modelname)
    if retrieved_instance:
        answer = retrieved_instance.gen(prompt.content)
        return {'content': answer }
    else:
        print("not found....")
        return {'content': "not found...." }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port= 8002)

