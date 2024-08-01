import re
from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId

# Custom ObjectId validator for Pydantic models
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
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

# Base model for User
class UserBase(BaseModel):
    username: str = Field(..., max_length=30)
    email: EmailStr

# Model for creating a new user
class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$",
        description="Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character."
    )
    profile_picture_url: Optional[str] = None

    @validator("password")
    def validate_password(cls, value):
        if not re.match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$", value):
            raise ValueError("Password must be at least 8 characters long and include an uppercase letter, a lowercase letter, a number, and a special character.")
        return value

# Model for returning user data
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

# Base model for Conversation
class ConversationBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    type: Optional[str] = None
    participants: List[PyObjectId]

# Model for creating a new conversation
class ConversationCreate(ConversationBase):
    pass

# Model for returning conversation data
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

# Base model for Message
class MessageBase(BaseModel):
    content: str
    attachments: Optional[List[dict]] = None

# Model for creating a new message
class MessageCreate(MessageBase):
    conversation_id: PyObjectId
    sender_id: PyObjectId

# Model for returning message data
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

# Models for password reset functionality
class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(
        ...,
        min_length=8,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]+$"
    )
