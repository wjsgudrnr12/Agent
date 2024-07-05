from fastapi import FastAPI

from models import *
from Processing.processprompt import *
from modulemanager import MainManager, classregistry
from Processing.processentries import *
from Processing.processrequest import *
from Module.gptmodule import gpt_4_submit


#중요 class 데코레이터 등록을 위해서 필요
import Module.vectordbmodule as vectordbmodule
import Module.llmmodule as llmmodule

mainmanager = MainManager()
app = FastAPI()  # FastAPI 애플리케이션 인스턴스

if __name__ == "__main__":

    args = argparse_argument()
    process_entries("llm", args.llm, mainmanager, classregistry)
    process_entries("vectordb", args.vectordb, mainmanager, classregistry)

# FastAPI 엔드포인트 함수
@app.post("/{organization}/{modulekind}/{modulename}/query")
async def query(organization: str, modulekind: str, modulename: str, query: Query):
    return await common_query_logic(mainmanager, organization, modulekind, modulename, query)


@app.post("/agent/query")
async def test(query: Query):
    # 공통 로직 함수를 호출
    organization = "ETRI"
    modulekind = "vectordb"
    modulename = "customdb"

    response_vectordb = await common_query_logic(mainmanager, organization, modulekind, modulename, query)

    organization = "ETRI"
    modulekind = "llm"
    modulename = "koalpaca_12_8"

    response_llm = await common_query_logic(mainmanager, organization, modulekind, modulename, query)

    # 두 응답을 하나의 JSON 객체로 합치기
    combined_response = {
        "vectordb_response": response_vectordb,
        "llm_response": response_llm
    }

    context_prompt = get_prompt(combined_response)
    gpt4result = gpt_4_submit(context_prompt)

    queryresult = {"context_prompt":context_prompt, "gpt_result": gpt4result}
    
    return queryresult
               

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port= 8000)