import requests
from fastapi import HTTPException
from Modules.module_manager import Module
from Modules.module_manager import classregistry
from Processing.process_request import *

@classregistry.register('ETRI_vectordb', )
class VectorDBModule():
    def __init__(self, org_name, ip, port, db_names_files, manager):
        self.org_name = org_name
        self.ip = ip
        self.port = port
        self.db_names_files = db_names_files
        self.manager = manager
#        self.is_loading = 0

    def load(self):
  
        db_info_list = self.db_names_files.split(',')
        for db_info in db_info_list:
            db_name, file_name = db_info.split(':')
            targeturi = "http://{}:{}/{}/load".format(self.ip, self.port, db_name)    
            print(targeturi)

            payload = {"path": file_name}
            print(payload)

            response = requesthandler(targeturi, payload)
        return("vectordb loading ok")

    def query(self, dbname, query):
        
        targeturi = "http://{}:{}/{}/query".format(self.ip, self.port, dbname)
        print(targeturi)    

        payload = {"query": query.query, "top_k":query.top_k}
        print(payload)

        response = requesthandler(targeturi, payload)
        return(response)