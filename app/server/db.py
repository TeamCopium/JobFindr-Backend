import motor.motor_asyncio
from bson.objectid import ObjectId
from models.user import User
# MONGO_URI = "mongodb+srv://User:User@cluster0.xgg1s.mongodb.net/jobfindr?retryWrites=true&w=majority"
MONGO_URI = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)

database = client.jobfindr
users = database.get_collection('Users')

async def getUsers():
    return await users.find()