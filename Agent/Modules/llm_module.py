import requests
from fastapi import HTTPException
from Modules.module_manager import Module
from Modules.module_manager import classregistry
from Processing.process_request import *

@classregistry.register('ETRI_llm', )
class LLMModule():
    def __init__(self, org_name, ip, port, llm_names_files, manager):
        self.org_name = org_name
        self.ip = ip
        self.port = port
        self.llm_names_files = llm_names_files
        self.manager = manager
#        self.is_loading = 0

    def load(self):
  
        llm_info_list = self.llm_names_files.split(',')
        for llm_info in llm_info_list:
            llm_name = llm_info
            targeturi = "http://{}:{}/{}/load".format(self.ip, self.port, llm_name)    
            print(targeturi)

            response = requesthandler(targeturi)
        return(f"{self.org_name} loading ok")

    def query(self, llmname, query):
        
        targeturi = "http://{}:{}/{}/query".format(self.ip, self.port, llmname)
        print(targeturi)    

        payload = {"content": query.query}
        print(payload)

        response = requesthandler(targeturi, payload)
        return(response)