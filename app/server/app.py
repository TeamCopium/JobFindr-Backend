###################################################################################################################################
#importing module
###################################################################################################################################

from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
# from pymongo import MongoClient
import motor.motor_asyncio
from passlib.context import CryptContext
import jwt
import datetime
from pyresparser import ResumeParser
from decouple import config

JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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

#################################################################################################################################
# SCHEMAS FOR MONGOOSE DATABASE
#################################################################################################################################
class User(BaseModel):
    id: str
    email: str
    password: str
    name: str
class NewUser(BaseModel):
    email: str
    password: str
    name: str

class Organization(BaseModel):
    email:str
    password:str
    name: str

class Job(BaseModel):
    description: str
    skills : list
    organization : str
    contact_email : str


#####################################################################################################################################
# token generation 
#####################################################################################################################################
def signJwt(user):
    payload = {
        'id': user['id'],
        'email': user['email'],
        'exp': datetime.utcnow() + 600
    }
    return jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)


#####################################################################################################################################
#testing route
#####################################################################################################################################
@app.get('/')
def index():
  return {'message' : 'Hello from server'}

#####################################################################################################################################
# user db functions 
#####################################################################################################################################

async def create_user(user):
    document = user
    user_exists = await fetch_one_user(document['email'])
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")
    document['password'] = pwd_context.hash(document['password'])
    result = await db.users.insert_one(document)
    document['id'] = str(document['_id'])
    del document['_id']
    return document

####################################################################################################################################
async def fetch_all_users():
    users = []
    cursor = db.users.find({})
    async for document in cursor:
        document['id'] = str(document['_id'])
        users.append(User(**document))
    return users


####################################################################################################################################
async def fetch_one_user(email):
    document = await db.users.find_one({"email": email})
    return document

####################################################################################################################################
async def update_user(email, name, password):
    await db.users.update_one({"email": email}, {"$set": {"name": name, "password": password}})
    document = await db.users.find_one({"email": email})
    return document

####################################################################################################################################
async def remove_user(email):
    await db.users.delete_one({"email": email})
    return True

####################################################################################################################################
async def fetch_one_organization(email):
    document = await db.organizations.find_one({"email": email})
    return document


#####################################################################################################################################
async def fetch_all_organizations():
    organizations = []
    cursor = db.organizations.find({})
    async for document in cursor:
        document['id'] = str(document['_id'])
        organizations.append(Organization(**document))
    return organizations

#####################################################################################################################################
async def create_organization(organization):
    document = organization
    organization_exists = await fetch_one_organization(document['email'])
    if organization_exists:
        raise HTTPException(status_code=400, detail="Organization already exists")
    document['password'] = pwd_context.hash(document['password'])
    result = await db.organizations.insert_one(document)
    document['id'] = str(document['_id'])
    del document['_id']
    return document


######################################################################################################################################
# user routes 
@app.get('/api/users/')
async def get_users():
    response = await fetch_all_users()
    return response

######################################################################################################################################
@app.get('/api/users/{email}')
async def get_user(email):
    response = await fetch_one_user(email)
    if response:
        return response
    raise HTTPException(404, f"There is no user with the email {email}")


######################################################################################################################################
@app.put('/api/users/{email}')
async def put_user(email: str, name: str, password: str):
    response = await update_user(email, name, password)
    if response:
        return response
    raise HTTPException(404, f"There is no user with the email {email}")

#####################################################################################################################################
@app.post("/api/register/user", response_model=User)
async def register_user(user: NewUser):
    response = await create_user(user.dict())
    if response:# org routes
        return response
    raise HTTPException(400, "Something went wrong")

#####################################################################################################################################
@app.post("/api/login/user", response_model=User)
async def login_user(email,password):
    response = await fetch_one_user(email)
    if response:
      if pwd_context.verify(password, response['password']):
        response['id'] = str(response['_id'])
        del response['_id']
        return response
      raise HTTPException(400, "Password is incorrect")
    raise HTTPException(404, f"There is no user with the email {email}") 

#####################################################################################################################################
@app.delete('/api/users/{email}')
async def delete_user(email):
    response = await remove_user(email)
    if response:
        return "Successfully deleted user"
    raise HTTPException(404, f"There is no user with the email {email}")

######################################################################################################################################
# org db functions 
######################################################################################################################################

@app.post('/api/register/organization', response_model=Organization)
def register_organization(organization: Organization):
    response = create_organization(organization.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")
@app.post('/api/login/organization', response_model=Organization)
def login_organization(email,password):
    response = fetch_one_organization(email)
    if response:
      if pwd_context.verify(password, response['password']):
        response['id'] = str(response['_id'])
        del response['_id']
        return response
      raise HTTPException(400, "Password is incorrect")
    raise HTTPException(404, f"There is no organization with the email {email}")

#####################################################################################################################################
# skills extract 
#####################################################################################################################################
@app.get("/api/skills")
async def get_skills():
    data = ResumeParser('/home/cyrus/Desktop/TeamCopium_JobFindr/app/server/DivyanshuKaushik_Resume.docx').get_extracted_data()
    print(data['skills'])
    return True


####################################################################################################################################