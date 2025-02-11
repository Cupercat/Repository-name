from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect # type: ignore # type: ignore
from sqlalchemy import select # type: ignore
from sqlalchemy.orm import selectinload # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession # type: ignore

from .webscocketConnect import manager # type: ignore
from src.db import get_session # type: ignore

from src.get_current_me import get_current_user, get_current_user_ws # type: ignore

from src.models.UserModel import User # type: ignore
from src.models.ChatModel import Chat, Message # type: ignore

from src.db import session # type: ignore


app = APIRouter(prefix="/chat", tags=["chat"])

@app.get("/chats")
async def get_chats(user:User = Depends(get_current_user), session:AsyncSession = Depends(get_session)):

    chats = await session.scalars(select(Chat).where((Chat.user1_id == user.id )| (Chat.user2_id == user.id)))
    return chats.all()



@app.post("/chats/create")
async def create_chat(user2_id:int, user:User = Depends(get_current_user), session:AsyncSession = Depends(get_session)):
    
    chat = Chat(user1_id=user.id, user2_id=user2_id)
    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return chat


@app.get("/chat/{chat_id}")
async def get_chat(chat_id:int,
                   user:User = Depends(get_current_user),
                   session:AsyncSession = Depends(get_session)):
    chat = await session.scalar(select(Chat)
                                .where(Chat.id == chat_id,
                                       (Chat.user1_id == user.id) | (Chat.user2_id == user.id))
                                .options(selectinload(Chat.messages)))
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat



@app.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    chat_id: int, 
    user: User = Depends(get_current_user_ws), 
    session1:AsyncSession = Depends(get_session)
):
    chat = await session1.scalar(select(Chat).where(Chat.id == chat_id))
    if not chat:
        await websocket.close()
        return
    
    await manager.connect(websocket, chat_id, user.id)
    
    try:
        while True:
            data = await websocket.receive_text()
            
            message = Message(chat_id=chat.id,  text=data)
            async with session() as connection:
                connection.add(message)
                await connection.commit()
                await connection.refresh(message)
            
            # Отправляем сообщение всем подключенным пользователям
            await manager.broadcast(
                {
                    "message_id": message.id,
                    "sender_id":user.id,
                    "message": message.text,
                },
                chat_id
            )
    except WebSocketDisconnect:
        
        await manager.disconnect(websocket, chat_id)
        print(f"Client disconnected from chat {chat_id}")@app.websocket("/ws/chat/{chat_id}")