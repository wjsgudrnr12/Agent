
from openai import OpenAI
import json
import types

from APIs.google_api import *
from Processing.process_prompt import *
from Processing.messages import *
from Processing.process_request import *
from fastapi import FastAPI

from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def gpt_func_call(messages, temperature=0, max_tokens=1024):
    functions = [
        {
            "name": "extract_google_search",
            "description": "구글에서 코드와 관련된 정보를 검색합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "구글에서 검색할 키워드"
                    }
                },
                "required": ["keyword"]
            }
        },
        {
            "name": "common_query_module",
            "description": "React가 뭐야?",

            "parameters": {
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "모듈을 검색할 조직이나 회사 이름",
                        "enum": ["ETRI", "KIST"],
                        "default": "ETRI"
                    },
                    "modulekind": {
                        "type": "string",
                        "description": "모듈의 종류",
                        "default": "vectordb"
                    },
                    "modulename": {
                        "type": "string",
                        "description": "모듈의 이름",
                        "enum": ["customdb", "chromadb"],
                        "default": "customdb"
                    }
                },
                "required": ["organization","modulekind", "modulename"] 
            }
        },
        {
            "name": "common_query_module",
#            "description": "LLM에서 코드를 생성합니다.",
            "description": "혁신적인 기술을 보셨다고 하셨는데, 어떤 기술이었나요?",
            "parameters": {
                "type": "object",
                "properties": {
                    "organization": {
                        "type": "string",
                        "description": "모듈을 검색할 조직이나 회사 이름",
                        "enum": ["ETRI", "KIST"],
                        "default": "ETRI"
                    },
                    "modulekind": {
                        "type": "string",
                        "description": "모듈의 종류",
                        "default": "llm"
                    },
                    "modulename": {
                        "type": "string",
                        "description": "모듈의 이름",
                        "default": "koalpaca_12_8"
                    }
                },
                "required": ["organization","modulekind", "modulename"] 
            }
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        functions=functions,
        function_call="auto",
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return completion.choices[0].message
    

def print_global_function_names():
    # globals()에서 모든 전역 항목을 가져옵니다.
    global_items = globals()
    
    # 함수만 골라내기
    for name, obj in global_items.items():
        if isinstance(obj, types.FunctionType):
            print(name)


'''
# execute_func_call 함수를 비동기로 변경하고 내부 로직 수정
async def execute_func_call(mainmanager, query):
    func_name = 'common_query_logic'  # 예시로 사용
    if func_name in globals():
        func_to_call = globals()[func_name]
        if func_name == 'common_query_logic':
            results = await common_query_logic(mainmanager, "ETRI", "llm", "koalpaca_12_8", query)
            return results  # 결과를 반환
        else:
            print("Function not implemented for dynamic calling.")
    else:
        print("Function not found in globals.")
'''

async def execute_func_call(mainmanager, query):
    print(f"\nquery = {query.query}")
    
    func_call_prompt = get_func_call_prompt(query)
    print(f"\nfunc_call_prompt = {func_call_prompt}")

    func_call_message = get_func_call_message(func_call_prompt)
    print(f"\nfunc_call_message = {func_call_message}")

    result = gpt_func_call(func_call_message)
    print(f"\nfunc_call_result = {result}")

    func_name = result.function_call.name  # 이미 문자열이므로 직접 할당
    arguments = json.loads(result.function_call.arguments)  # 문자열 내 JSON 데이터 파싱

    # globals()를 사용하여 함수가 정의된 전역 네임스페이스에서 함수 이름을 검색합니다.
    if func_name in globals():
        # globals()에서 직접 함수 객체를 가져옵니다.
        func_to_call = globals()[func_name]
        # 함수를 인자와 함께 호출합니다.
        if func_name == 'extract_google_search':
            results = func_to_call(arguments['keyword'])
            return results
        
        elif func_name == 'common_query_module':
#            results = await common_query_logic(mainmanager, "ETRI", "llm", "koalpaca_12_8", query)

#            results = await func_to_call(mainmanager, "ETRI", "llm", "koalpaca_12_8", query)
            results = await func_to_call(mainmanager, arguments['organization'], arguments['modulekind'], arguments['modulename'], query)
#            print(json.dumps(results, indent=2))
            return results
        
        else:
            # 다른 함수 호출 구현이 필요할 수 있습니다.
            print("Function not implemented for dynamic calling.")
    else:
        print(f"No method named {func_name} is defined in the global scope.")


if __name__ == '__main__':

    posting1 = """python으로 작성된 계산기 코드를 검색해줘"""
    posting2 = """KIST에서 milvus에서 데이터를 검색해줘"""
    posting3 = """koalpaca_12_8에서 코드를 생성해 줘"""

    execute_func_call(posting3)
