from pydantic import BaseModel, Field

class VectorDBQuery(BaseModel):
    query: str
    top_k: int

class File(BaseModel):
    path: str

class Query(BaseModel):
    collection_name: str = Field(None, examples=["leetcode"], description= "select the specific DB collection")
    filename: str = Field(None, example="\"filename\": \"sample.pdf\"", description="Select a specific file")
    query: str = Field(None, description="query to vectordb")
    top_k: int = Field(1, description="select top_k answers")
