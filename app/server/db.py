import motor.motor_asyncio
from app.server.model import User
# MONGO_URI = "mongodb+srv://User:User@cluster0.xgg1s.mongodb.net/jobfindr?retryWrites=true&w=majority"
MONGO_URI = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

database = client.Jobfindr
users = database.users

async def get_users():
    return await users.find()
async def create_user(email,password):
    return email
def check():
    return 'hello'
