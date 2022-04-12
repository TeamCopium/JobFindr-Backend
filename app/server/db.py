import motor.motor_asyncio
# MONGO_URI = "mongodb+srv://User:User@cluster0.xgg1s.mongodb.net/jobfindr?retryWrites=true&w=majority"
MONGO_URI = "mongodb://localhost:27017"

client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://localhost:27017/')
db = client.jobfindr
