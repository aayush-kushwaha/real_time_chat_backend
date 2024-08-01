import re
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, schema):
        schema.update({
            'type': 'string',
            'format': 'objectid',
            'example': '60b8d2958f62ce5e7f43e57c'
        })

# Define a Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Define a TokenData model for additional token-related information
class TokenData(BaseModel):
    username: Optional[str] = None

# Base model for User
class UserBase(BaseModel):
    username: str = Field(..., max_length=30)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        pattern=r"^[A-Za-z\d@$!%*?&]+$",  # Simplified pattern
        description="Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character."
    )
    profile_picture_url: Optional[str] = None

    @validator("password")
    def validate_password(cls, value):
        # Custom validation logic
        if (not re.search(r"[A-Z]", value) or
            not re.search(r"[a-z]", value) or
            not re.search(r"\d", value) or
            not re.search(r"[@$!%*?&]", value)):
            raise ValueError("Password must include an uppercase letter, a lowercase letter, a number, and a special character.")
        return value

class User(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: str
    profile_picture_url: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: Optional[bool] = True
    verified: Optional[bool] = False

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class ConversationBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    type: Optional[str] = None
    participants: List[PyObjectId]

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    created_at: datetime
    last_updated: datetime
    muted_users: Optional[List[PyObjectId]] = None

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class MessageBase(BaseModel):
    content: str
    attachments: Optional[List[dict]] = None

class MessageCreate(MessageBase):
    conversation_id: PyObjectId
    sender_id: PyObjectId

class Message(MessageBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    conversation_id: PyObjectId
    sender_id: PyObjectId
    timestamp: datetime
    read_by: Optional[List[PyObjectId]] = []
    reactions: Optional[Dict[PyObjectId, str]] = {}
    edited_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    class Config:
        json_encoders = {
            ObjectId: str,
            datetime: lambda v: v.isoformat()
        }

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(
        ...,
        min_length=8,
        pattern=r"^[A-Za-z\d@$!%*?&]+$",  # Simplified pattern
        description="New password must be at least 8 characters long."
    )

    @validator("new_password")
    def validate_new_password(cls, value):
        if (not re.search(r"[A-Z]", value) or
            not re.search(r"[a-z]", value) or
            not re.search(r"\d", value) or
            not re.search(r"[@$!%*?&]", value)):
            raise ValueError("New password must include an uppercase letter, a lowercase letter, a number, and a special character.")
        return value
