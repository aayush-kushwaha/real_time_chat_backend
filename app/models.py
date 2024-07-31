from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
from datetime import datetime

DATABASE_URL = "mongodb://localhost:27017"
client = AsyncIOMotorClient(DATABASE_URL)
db = client["chatapp"]

def get_user_collection():
    return db["users"]

def get_conversation_collection():
    return db["conversations"]

def get_message_collection():
    return db["messages"]

# Create indexes for text search and unique constraints
async def create_indexes():
    await db["users"].create_index([("username", ASCENDING)], unique=True)
    await db["users"].create_index([("email", ASCENDING)], unique=True)
    await db["messages"].create_index([("content", "text")])
    await db["messages"].create_index([("conversation_id", ASCENDING)])
    await db["messages"].create_index([("sender_id", ASCENDING)])
    await db["messages"].create_index([("timestamp", DESCENDING)])
    await db["conversations"].create_index([("created_at", DESCENDING)])
    await db["conversations"].create_index([("last_updated", DESCENDING)])
