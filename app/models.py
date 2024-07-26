from motor.motor_asyncio import AsyncIOMotorClient

DATABASE_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(DATABASE_URL)
db = client["messengerdb"]

def get_user_collection():
    return db["users"]

def get_conversation_collection():
    return db["conversations"]

def get_message_collection():
    return db["messages"]
