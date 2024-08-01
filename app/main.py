from fastapi import FastAPI, Depends, HTTPException, status, WebSocket, WebSocketDisconnect
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from schemas import UserCreate, User, Token, ConversationCreate, Conversation, MessageCreate, Message, PasswordResetRequest, PasswordReset
from crud import create_user, get_user_by_id, create_conversation, get_conversation, create_message, get_messages, generate_password_reset_token, reset_password
from auth import create_access_token, authenticate_user, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from websocket import manager
from datetime import timedelta
from bson import ObjectId
import uvicorn

app = FastAPI()

@app.post("/users/register", response_model=User)
async def register_user(user_create: UserCreate):
    user = await create_user(user_create)
    return user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: ObjectId, current_user: User = Depends(get_current_user)):
    user = await get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.post("/conversations", response_model=Conversation)
async def create_conversation(conversation_create: ConversationCreate):
    conversation = await create_conversation(conversation_create)
    return conversation

@app.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: ObjectId):
    conversation = await get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@app.post("/messages", response_model=Message)
async def create_message(message_create: MessageCreate):
    message = await create_message(message_create)
    return message

@app.get("/conversations/{conversation_id}/messages", response_model=List[Message])
async def get_messages(conversation_id: ObjectId, limit: int = 20, skip: int = 0):
    messages = await get_messages(conversation_id, limit, skip)
    return messages

@app.post("/password-reset-request")
async def password_reset_request(request: PasswordResetRequest):
    token = await generate_password_reset_token(request.email)
    if token:
        # Here you would send the email with the reset link including the token
        return {"msg": "Password reset email sent"}
    return {"msg": "User not found"}, 404

@app.post("/password-reset")
async def password_reset(reset: PasswordReset):
    success = await reset_password(reset.token, reset.new_password)
    if success:
        return {"msg": "Password has been reset"}
    return {"msg": "Invalid or expired token"}, 400

@app.websocket("/ws/{conversation_id}")
async def websocket_endpoint(conversation_id: ObjectId, websocket: WebSocket):
    await manager.connect(conversation_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = Message.parse_raw(data)
            await manager.broadcast(conversation_id, message)
    except WebSocketDisconnect:
        manager.disconnect(conversation_id, websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
