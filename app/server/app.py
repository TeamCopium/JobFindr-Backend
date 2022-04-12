from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from pymongo import MongoClient
import motor.motor_asyncio
from bson import ObjectId
import json
import os

app = FastAPI()

origins = ['http://localhost:3000']

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# mongo setup 
# MONGO_URI = "mongodb://localhost:27017"
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/')
db = client.jobfindr

# schemas 
class User(BaseModel):
    id: str
    email: str
    password: str
    name: str

@app.get('/')
def index():
  return {'message' : 'Hello from server'}

# user db functions 
async def create_user(user):
    document = user
    result = await db.users.insert_one(document)
    return document
async def fetch_all_users():
    users = []
    cursor = db.users.find({})
    async for document in cursor:
        document['id'] = str(document['_id'])
        users.append(User(**document))
    return users
async def fetch_one_user(email):
    document = await db.users.find_one({"email": email})
    return document

async def update_user(email, name, password):
    await db.users.update_one({"email": email}, {"$set": {"name": name, "password": password}})
    document = await db.users.find_one({"email": email})
    return document

async def remove_user(email):
    await db.users.delete_one({"email": email})
    return True

# user routes 
@app.get('/api/users/')
async def get_users():
    response = await fetch_all_users()
    return response
@app.get('/api/users/{email}')
async def get_user(email):
    response = await fetch_one_user(email)
    if response:
        return response
    raise HTTPException(404, f"There is no user with the email {email}")

@app.put('/api/users/{email}')
async def put_user(email: str, name: str, password: str):
    response = await update_user(email, name, password)
    if response:
        return response
    raise HTTPException(404, f"There is no user with the email {email}")
@app.post("/api/register/", response_model=User)
async def register_user(user: User):
    response = await create_user(user.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")
@app.post("/api/login/", response_model=User)
async def login_user(email,password):
    response = await fetch_one_user(email)
    if response:
        if response['password'] == password:
            response['id'] = str(response['_id'])
            del response['_id']
            return response
        raise HTTPException(400, "Password is incorrect")
    raise HTTPException(404, f"There is no user with the email {email}")
@app.delete('/api/users/{email}')
async def delete_user(email):
    response = await remove_user(email)
    if response:
        return "Successfully deleted user"
    raise HTTPException(404, f"There is no user with the email {email}")

# skills extract 
import docx2txt
import nltk
import requests
 
nltk.download('stopwords')
 
 
def extract_text_from_docx(docx_path):
    txt = docx2txt.process(docx_path)
    if txt:
        return txt.replace('\t', ' ')
    return None
 
 
def skill_exists(skill):
    url = f'https://api.apilayer.com/skills?q={skill}&amp;count=1'
    headers = {'apikey': 'tegtTot9eJxbtD7lxSoZPnGgR08dYYzo'}
    response = requests.request('GET', url, headers=headers)
    result = response.json()
 
    if response.status_code == 200:
        return len(result) > 0 and result[0].lower() == skill.lower()
    raise Exception(result.get('message'))
 
 
def extract_skills(input_text):
    stop_words = set(nltk.corpus.stopwords.words('english'))
    word_tokens = nltk.tokenize.word_tokenize(input_text)

    filtered_tokens = [w for w in word_tokens if w not in stop_words]

    filtered_tokens = [w for w in word_tokens if w.isalpha()]

    bigrams_trigrams = list(map(' '.join, nltk.everygrams(filtered_tokens, 2, 3)))
 
    found_skills = set()

    for token in filtered_tokens:
        if skill_exists(token.lower()):
            found_skills.add(token)
 
    for ngram in bigrams_trigrams:
        if skill_exists(ngram.lower()):
            found_skills.add(ngram)
 
    return found_skills

@app.get("/api/skills")
async def get_skills():
    text = extract_text_from_docx(os.path.dirname(os.path.abspath(__file__))+"/resume.docx")
    skills = extract_skills(text)
 
    print(skills)
    # print()
    return True