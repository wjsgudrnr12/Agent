from fastapi import UploadFile, Query
from pydantic import BaseModel, Field
from enum import Enum
from typing import Literal, Optional, Union

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
    collection_name: str = Field(None, examples=["leetcode"], description= "select the specific DB collection")
    filename: str = Field(None, example="\"filename\": \"sample.pdf\"", description="Select a specific file")
    query: str = Field(None, description="query to vectordb")
    top_k: int = Field(None, description="select top_k answers")

class Solution(BaseModel):
    id: str | None = None
    collection: str
    problem_id: str