from fastapi import UploadFile, Query
from pydantic import BaseModel, Field
from enum import Enum

class VectorEnum(str, Enum):
    chromadb = "chromadb"
    customdb = "customdb"
    milvusdb = "milvusdb"

class CollectionEnum(Enum):
    leetcode = "leetcode"
    grepp = "grepp"
    robotics = "robotics"
    suresoft = "suresoft"
    solutions = "solutions"  

class Metadata(BaseModel):
    filename: str
    page: int

class Document(BaseModel):
    id: str
    text: str
    metadata: Metadata

class File(UploadFile):
    path: str

class Query(BaseModel):
    query: str
    top_k: int

class Solution(BaseModel):
    id: str | None = None
    collection: str
    problem_id: str