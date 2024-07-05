import requests
import json
from models import *

 # vectordb -> http://127.0.0.1:8000/ETRI/vectordb/customdb/query   
 # llm ->http://127.0.0.1:8000/ETRI/llm/koalpaca_12_8/query
async def common_query_logic(mainmanager, organization: str, modulekind: str, modulename: str, query: Query):
    manager = mainmanager.get_manager(modulekind)
    if manager:
        module_name = f"{organization}_{modulekind}"
        module = manager.get_module(module_name)
        if module:
            response = module.query(modulename, query)
            decoded_content = response.content.decode('utf-8')
            decoded_dict = json.loads(decoded_content)
            return decoded_dict
        else:
            print("'content': 'The vectordb you requested does not exist.'")
            return {'content': "The vectordb you requested does not exist."}
        

def requesthandler(targeturi, payload=None):
    try:
        if payload == None:
            response = requests.get(targeturi)                    
        else:
            response = requests.post(targeturi, json=payload)                
        
        response.raise_for_status()  # Raise an exception for HTTP error codes
    
    except requests.exceptions.ConnectionError as e:
        print(f"Connection error occurred: {e}")
        # 예외 처리 코드 작성
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        # 예외 처리 코드 작성
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        # 예외 처리 코드 작성
    else:
        # 요청이 성공했을 때의 코드 작성
        print("Request succeeded")
        print(response.json())
    
        return(response)
