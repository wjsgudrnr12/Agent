from pydantic import BaseModel

class Prompt(BaseModel):
  content: str

class Answer(BaseModel):
  content: str