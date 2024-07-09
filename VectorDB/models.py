from fastapi import UploadFile, Query
from pydantic import BaseModel, Field
from enum import Enum
<<<<<<< HEAD
from typing import Dict, Any, Optional, Literal
=======
from typing import Literal, Optional, Union
>>>>>>> 227e3e2... fix: path to object upload & add collection parameter

class VectorEnum(str, Enum):
    chromadb = "chromadb"
    customdb = "customdb"
    milvusdb = "milvusdb"

class CollectionEnum(Enum):
    leetcode = "leetcode"
    grepp = "grepp"
    robotics = "robotics"
    suresoft = "suresoft"
<<<<<<< HEAD
    humaneval = "humaneval"
=======
>>>>>>> 227e3e2... fix: path to object upload & add collection parameter
    solutions = "solutions"  

class Metadata(BaseModel):
    filename: str
    page: int

class Document(BaseModel):
    id: str
    text: str
    metadata: Metadata
<<<<<<< HEAD

<<<<<<< HEAD
=======
>>>>>>> 36e8697... This is a version that adds function call functionality and resovling conflicts.
'''
class File(UploadFile):
    path: str
'''
class File(BaseModel):
=======
class File(UploadFile):
>>>>>>> 227e3e2... fix: path to object upload & add collection parameter
    path: str
    
class Query(BaseModel):
    query: str
    top_k: int

<<<<<<< HEAD
class Data(BaseModel):
    data: Dict[str, Any]

class FieldSchema(BaseModel):
    name: str
    dtype: Literal["NONE", "BOOL", "INT8", "INT16", "INT32", "INT64", "FLOAT", "DOUBLE", "STRING", "VARCHAR", "ARRAY", "JSON", "BINARY_VECTOR", "FLOAT_VECTOR", "FLOAT16_VECTOR", "BFLOAT16_VECTOR", "SPARSE_FLOAT_VECTOR", "UNKNOWN"]
    max_length: Optional[int] = None
    is_primary: Optional[bool] = None
    dim: Optional[str] = None
    class Config:
        schema_extra = {
            "example": [
                {
                    "name": "field1",
                    "dtype": "string",
                    "max_length": 255,
                    "is_primary": True,
                },
                {
                    "name": "field2",
                    "dtype": "integer",
                    "max_length": 10,
                    "is_primary": False,
                    "dim": "example_dim"
                }
            ]
        }
=======
class Solution(BaseModel):
    id: str | None = None
    collection: str
    problem_id: str
>>>>>>> 227e3e2... fix: path to object upload & add collection parameter
