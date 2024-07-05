from pydantic import BaseModel, Field

class Metadata(BaseModel):
    filename: str
    page: int

class Document(BaseModel):
    id: str
    text: str
    metadata: Metadata

class File(BaseModel):
    path: str

class Query(BaseModel):
    collection_name: str = Field(None, examples=["leetcode"], description= "select the specific DB collection")
    filename: str = Field(None, example="\"filename\": \"sample.pdf\"", description="Select a specific file")
    query: str = Field(None, description="query to vectordb")
    top_k: int = Field(None, description="select top_k answers")

# class MilvusdbQuery(BaseModel):
#     collection_name: str = Field(None, examples=["leetcode"], description= "select the specific DB collection")
#     filename: str 
#     query: str
#     top_k: int

class Solution(BaseModel):
    id: str | None = None
    collection: str
    problem_id: str