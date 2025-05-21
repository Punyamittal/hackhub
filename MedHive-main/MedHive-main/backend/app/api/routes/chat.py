from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from groq import Groq
from pydantic import BaseModel
from datetime import datetime
import uuid

from app.db.session import get_db
from app.core.config import settings
from app.models.chat import ChatHistory
from app.models.user import User
from app.api.routes.auth import get_current_user

router = APIRouter()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    stream: bool = False

class ChatResponse(BaseModel):
    message: ChatMessage
    conversation_id: str

@router.post("/send", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    Send a message to the Groq-powered assistant and get a response.
    Also stores the conversation in the database for the current user.
    """
    
    if not settings.GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="GROQ API key not configured")
    
    # Initialize the Groq client
    client = Groq(api_key=settings.GROQ_API_KEY)
    
    try:
        # Add a medical-specific system message
        system_message = {
            "role": "system",
            "content": "You are HachathonHub's AI assistant - a helpful and informative healthcare companion. \
                      Provide accurate medical information while always clarifying that you're not a doctor \
                      and encouraging users to seek professional medical advice for health concerns. \
                      You should focus on providing evidence-based information, explaining medical concepts \
                      in accessible language, and helping users navigate the HachathonHub platform."
        }
        
        # Prepare the messages for the Groq API
        groq_messages = [system_message] + [msg.dict() for msg in request.messages]
        
        # Get the completion from Groq
        completion = client.chat.completions.create(
            messages=groq_messages,
            model="llama3-70b-8192",
            temperature=0.5,
            max_tokens=1024,
            stream=request.stream
        )
        
        # Get the response
        assistant_response = completion.choices[0].message
        
        # Create a response for the frontend
        response = ChatResponse(
            message=ChatMessage(
                role="assistant",
                content=assistant_response.content
            ),
            conversation_id=str(uuid.uuid4())
        )
        
        # Store the conversation in the database asynchronously
        if current_user:
            # Store the user's message
            user_message = ChatHistory(
                user_id=current_user.id,
                message=request.messages[-1].content,
                is_user=True
            )
            db.add(user_message)
            
            # Store the assistant's response
            assistant_message = ChatHistory(
                user_id=current_user.id,
                message=assistant_response.content,
                is_user=False
            )
            db.add(assistant_message)
            db.commit()
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error communicating with Groq API: {str(e)}")

@router.get("/history")
async def get_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the chat history for the current user
    """
    history = db.query(ChatHistory).filter(ChatHistory.user_id == current_user.id).order_by(ChatHistory.created_at).all()
    
    # Convert to a list of message pairs (user message + assistant response)
    formatted_history = []
    for i in range(0, len(history), 2):
        if i + 1 < len(history):
            formatted_history.append({
                "user_message": history[i].message,
                "assistant_message": history[i+1].message,
                "timestamp": history[i].created_at.isoformat()
            })
    
    return {"history": formatted_history} 