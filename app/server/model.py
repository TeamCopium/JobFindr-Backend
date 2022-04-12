from pydantic import BaseModel

class User(BaseModel):
    name:str

class Todo(BaseModel):
    title: str
    description: str