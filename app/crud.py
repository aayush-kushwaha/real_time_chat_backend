from .models import get_user_collection, get_conversation_collection, get_message_collection
from .schemas import UserCreate, User, ConversationCreate, Conversation, MessageCreate, Message
from .utils import hash_password
from datetime import datetime
from bson import ObjectId
import uuid

async def create_user(user_create: UserCreate):
    user_collection = get_user_collection()
    hashed_password = hash_password(user_create.password)
    user = User(
        username=user_create.username,
        hashed_password=hashed_password,
        profile_picture_url=user_create.profile_picture_url,
        created_at=datetime.utcnow(),
        email=user_create.email,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        bio=user_create.bio,
        last_login=None,
        is_active=True,
        verified=False
    )
    result = await user_collection.insert_one(user.dict(by_alias=True))
    user.id = result.inserted_id
    return user

async def get_user_by_username(username: str):
    user_collection = get_user_collection()
    user = await user_collection.find_one({"username": username})
    return user

async def get_user_by_id(user_id: ObjectId):
    user_collection = get_user_collection()
    user = await user_collection.find_one({"_id": user_id})
    return user

async def generate_password_reset_token(email: str):
    user_collection = get_user_collection()
    user = await user_collection.find_one({"email": email})
    if not user:
        return None
    reset_token = str(uuid.uuid4())
    await user_collection.update_one({"email": email}, {"$set": {"reset_token": reset_token}})
    return reset_token

async def reset_password(token: str, new_password: str):
    user_collection = get_user_collection()
    hashed_password = hash_password(new_password)
    result = await user_collection.update_one({"reset_token": token}, {"$set": {"hashed_password": hashed_password, "reset_token": None}})
    return result.modified_count > 0

async def create_conversation(conversation_create: ConversationCreate):
    conversation_collection = get_conversation_collection()
    conversation = Conversation(
        name=conversation_create.name,
        description=conversation_create.description,
        icon=conversation_create.icon,
        type=conversation_create.type,
        participants=conversation_create.participants,
        created_at=datetime.utcnow(),
        last_updated=datetime.utcnow(),
        muted_users=[]
    )
    result = await conversation_collection.insert_one(conversation.dict(by_alias=True))
    conversation.id = result.inserted_id
    return conversation

async def get_conversation(conversation_id: ObjectId):
    conversation_collection = get_conversation_collection()
    conversation = await conversation_collection.find_one({"_id": conversation_id})
    return conversation

async def create_message(message_create: MessageCreate):
    message_collection = get_message_collection()
    message = Message(
        conversation_id=message_create.conversation_id,
        sender_id=message_create.sender_id,
        content=message_create.content,
        attachments=message_create.attachments,
        timestamp=datetime.utcnow(),
        read_by=[],
        reactions={},
        edited_at=None,
        deleted_at=None
    )
    result = await message_collection.insert_one(message.dict(by_alias=True))
    message.id = result.inserted_id
    return message

async def get_messages(conversation_id: ObjectId, limit: int = 20, skip: int = 0):
    message_collection = get_message_collection()
    messages = await message_collection.find({"conversation_id": conversation_id}).sort("timestamp", -1).skip(skip).limit(limit).to_list(length=limit)
    return messages
