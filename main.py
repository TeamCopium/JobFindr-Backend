###################################################################################################################################
#importing module
###################################################################################################################################

from fastapi import FastAPI,HTTPException,File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId
import motor.motor_asyncio
from passlib.context import CryptContext
import jwt
import datetime
from pyresparser import ResumeParser
from decouple import config
import os
import shutil

# JWT_SECRET = config("secret")
# JWT_ALGORITHM = config("algorithm")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()

origins = ['http://localhost:3000',"*"]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# mongo setup 
MONGO_URI = "mongodb+srv://User:User@cluster0.xgg1s.mongodb.net/jobfindr?retryWrites=true&w=majority"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
db = client.jobfindr

#################################################################################################################################
# SCHEMAS FOR MONGOOSE DATABASE
#################################################################################################################################
class User(BaseModel):
    id: str
    email: str
    password: str
    name: str
    skills:list

class NewUser(BaseModel):
    email: str
    password: str
    name: str

class Organization(BaseModel):
    email:str
    password:str
    name: str

class Job(BaseModel):
    id: str
    title: str
    description: str
    skills : list
    organization : str
    contact_email : str

class NewJob(BaseModel):
    title: str
    description: str
    skills : list
    organization : str
    contact_email : str


#####################################################################################################################################
# token generation 
#####################################################################################################################################
# def signJwt(user):
#     payload = {
#         'id': user['id'],
#         'email': user['email'],
#         'exp': datetime.utcnow() + 600
#     }
#     return jwt.encode(payload, JWT_SECRET, JWT_ALGORITHM)

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
    user_exists = await fetch_one_user(document['email'],post=True)
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists")
    document['password'] = pwd_context.hash(document['password'])
    document['skills'] = []
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
async def add_skills(email, skills):
    await db.users.update_one({"email": email}, {"$set": {"skills": skills}})
    document = await db.users.find_one({"email": email})
    document['id'] = str(document['_id'])
    del document['_id']
    return document

####################################################################################################################################
async def fetch_one_user(email,post=False):
    document = await db.users.find_one({"email": email})
    if document:
      if post==False:
        document['_id'] = str(document['_id'])
      return document
    return False
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
async def fetch_one_organization(email,post=False):
    document = await db.organizations.find_one({"email": email})
    if post==False:
      document['_id'] = str(document['_id'])
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
    organization_exists = await fetch_one_organization(document['email'],post=True)
    if organization_exists:
        raise HTTPException(status_code=400, detail="Organization already exists")
    document['password'] = pwd_context.hash(document['password'])
    result = await db.organizations.insert_one(document)
    document['id'] = str(document['_id'])
    del document['_id']
    return document

async def fetch_one_job(id):
    document = await db.jobs.find_one({"_id": ObjectId(id)})
    document['id'] = str(document['_id'])
    del document['_id']
    return document
#################################################################################################################################
async def create_job(job):
    document = job
    skills = []
    for skill in document['skills']:
        skills.append(skill.lower())
    document['skills'] = skills
    result = await db.jobs.insert_one(document)
    document['id'] = str(document['_id'])
    del document['_id']
    return document
#################################################################################################################################
async def fetch_all_jobs():
    jobs = []
    cursor = db.jobs.find({})
    async for document in cursor:
        document['id'] = str(document['_id'])
        jobs.append(Job(**document))
    return jobs

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
async def register_organization(organization: Organization):
    response = await create_organization(organization.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")
@app.post('/api/login/organization', response_model=Organization)
async def login_organization(email,password):
    response = await fetch_one_organization(email)
    if response:
      if pwd_context.verify(password, response['password']):
        response['id'] = str(response['_id'])
        del response['_id']
        return response
      raise HTTPException(400, "Password is incorrect")
    raise HTTPException(404, f"There is no organization with the email {email}")
#####################################################################################################################################
@app.get('/api/organizations')
async def get_organizations():
    response = await fetch_all_organizations()
    return response
#####################################################################################################################################
@app.get('/api/organizations/{email}')
async def get_organization(email):
    response = await fetch_one_organization(email)
    if response:
        return response
    raise HTTPException(404, f"There is no organization with the email {email}")

#################################################################################################################################
# job routes 
#################################################################################################################################
@app.post('/api/createJob', response_model=Job)
async def add_job(job: NewJob):
    response = await create_job(job.dict())
    if response:
        return response
    raise HTTPException(400, "Something went wrong")

@app.get('/api/jobs/{email}')
async def get_jobs(email):
    user = await fetch_one_user(email)
    if user:
        response = await fetch_all_jobs()
        jobs = []
        for job in response:
            common = [value for value in user['skills'] if value in job.skills]
            if len(common) > 0:
                jobs.append(job)
        return jobs
    raise HTTPException(404, "User Not Found")

@app.get('/api/jobs')
async def get_jobs():
    response = await fetch_all_jobs()
    return response
@app.get('/api/job/{id}')
async def fetch_job(id):
    response = await fetch_one_job(id)
    if response:
        return response
    raise HTTPException(404, f"There is no job with the id {id}")

#################################################################################################################################
# file upload routes
#################################################################################################################################
@app.post("/api/uploadResume/{email}")
async def upload_file(email,file: UploadFile = File(...)):
  if file.content_type == 'application/pdf' or file.content_type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
    with open(f'{file.filename}', "wb") as buffer:
      shutil.copyfileobj(file.file, buffer)
      data = ResumeParser(file.filename).get_extracted_data()
      skills = []
      for skill in data['skills']:
        skills.append(skill.lower())
      await add_skills(email,skills)
      os.unlink(file.filename)
    return {"message":"Successfully uploaded file"}
  return {"message":"File type not supported"}