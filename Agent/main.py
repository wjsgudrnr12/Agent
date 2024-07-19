from fastapi import FastAPI

from Processing.models import *
from Processing.process_prompt import *
from Processing.process_entries import *
from Processing.process_request import *
from Modules.module_manager import MainManager, classregistry

from APIs.func_call_api import *
from APIs.gpt_api import *


#중요 class 데코레이터 등록을 위해서 필요
import Modules.vectordb_module as vectordb_module
import Modules.llm_module as llm_module

mainmanager = MainManager()
app = FastAPI()  # FastAPI 애플리케이션 인스턴스

if __name__ == "__main__":
    args = argparse_argument()
    process_entries("llm", args.llm, mainmanager, classregistry)
    process_entries("vectordb", args.vectordb, mainmanager, classregistry)

# FastAPI 엔드포인트 함수
@app.post("/{organization}/{modulekind}/{modulename}/query")
async def query(organization: str, modulekind: str, modulename: str, query: Query):
    return await common_query_module(mainmanager, organization, modulekind, modulename, query)


# Function call 엔드포인트 함수
@app.post("/agent/functioncall/query")
async def test(query: Query):
    return await execute_func_call(mainmanager, query)


# Function call 엔드포인트 함수
@app.post("/agent/query")
async def test(query: Query):

    process_messages = ["""python으로 작성된 계산기 코드를 검색해줘""",
                        """1980년대에 첫 번째 혁신적인 기술을 보셨다고 하셨는데, 어떤 기술이었나요?""",
                        """React가 뭐야?"""]
    
    process_query = Query()

    process_responses = []

    for process_message in process_messages: 
        process_query.query = process_message
        process_response = await execute_func_call(mainmanager, process_query)
        print(process_response)
        process_responses.append(process_response)  

    # 두 응답을 하나의 JSON 객체로 합치기
    combined_response = {
        "qoogle_response": process_responses[0],
        "vectordb_response": process_responses[1],
        "llm_response": process_responses[2]
    }
    print(" ---------------------------------------------------------------------- ")
    print(query.query)
    print(combined_response)

    query_prompt = get_query_context_prompt(query.query, combined_response)
    print(query_prompt)
    gpt4result = gpt_4_submit(query_prompt)

    queryresult = {"context_prompt":query_prompt, "gpt_result": gpt4result}

    return queryresult

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port= 8000)