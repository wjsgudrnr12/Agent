from fastapi import FastAPI
import locale
import uvicorn

from models import *
from module_manager import llm_load, llm_query

#중요 class 데코레이터 등록을 위해서 필요
from LLM.koalpaca.interence_koalpaca_12_8 import Koalpach_12_8_LLMModel

locale.getpreferredencoding = lambda: "UTF-8"

app = FastAPI()
#llmmodel = Koalpach_12_8_LLMModel()

@app.get('/')
async def chat():
    return 'Hello World!'

@app.get('/{modelname}/load')
async def load(modelname:str) -> Answer:
    return llm_load(modelname)


@app.post('/{modelname}/query')
async def query(modelname:str, prompt: Prompt) -> Answer:
    return llm_query(modelname, prompt)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port= 8002)

