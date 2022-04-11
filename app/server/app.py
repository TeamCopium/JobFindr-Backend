
from fastapi import FastAPI
from pydantic import BaseModel
# from db import (getUsers)
from pdfreader import (extract_text_from_docx)
app = FastAPI()

@app.get('/')
def index():
  return {'message' : 'Hello from server'}

@app.get('/users')
async def getUsers():
    # getUsers()
    extract_text_from_docx()
