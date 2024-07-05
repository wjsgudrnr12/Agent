import os
from PyPDF2 import PdfReader
from fastapi import FastAPI
from VectorDB.milvusdbmodule.milvus import Milvus
from models import Document, Query, File

class MilvusdbModule:
    def __init__(self):
        pass

    def some_method(self):
        pass

    def milvusdb_load(self, file: File):
        # ..
        return {}
    
    def milvusdb_query(self, collection_name, query: Query) -> list[Document]:
        collection = Milvus(f"{collection_name}")
        result = collection.search(query.filename, query.query, query.top_k)

        print(query.filename, query.query)
        return result
    