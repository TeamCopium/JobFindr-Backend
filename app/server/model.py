from pydantic import BaseModel


class User(BaseModel):
    id: str
    email: str
    password: str
    name: str

class Todo(BaseModel):
    title: str
    description: str