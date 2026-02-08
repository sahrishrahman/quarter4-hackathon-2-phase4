from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Tuple
from pydantic import BaseModel
from ..db import get_async_session
from ..agents.chat_agent import ChatAgent
from ..api.deps import ChatUserValidationDep
from typing import Optional
import logging

router = APIRouter(prefix="/chat", tags=["chat"])

# Request and response models
class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    conversation_id: str
    message: str
    task_operations: list
    timestamp: str


@router.post("/{user_id}", response_model=ChatResponse)
async def chat_endpoint(
    user_id: str,
    request: ChatRequest,
    user_email_data: ChatUserValidationDep,
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """
    Process a user's chat message and return an AI response with task operations.

    Args:
        user_id: The ID of the user making the request (path parameter)
        request: The chat request containing the message and optional conversation_id
        user_email_data: Tuple of (user_id, email) from validated JWT
        session: Database session

    Returns:
        ChatResponse with conversation_id, message, task_operations, and timestamp
    """
    print("request recieved")
    try:
        current_user_id, email = user_email_data

        # Log the received request for debugging
        logging.info(f"Chat endpoint called - user_id: {user_id}, current_user_id: {current_user_id}")
        logging.info(f"Request message: {request.message[:50]}...")
        logging.info(f"Request conversation_id: {request.conversation_id}")

        # Initialize the chat agent
        agent = ChatAgent()

        # Process the message using the agent
        result = await agent.process_message(
            session=session,
            user_id=current_user_id,  # Use validated user ID
            email=email,  # Use email from JWT
            message_content=request.message,
            conversation_id=request.conversation_id
        )

        return ChatResponse(
            conversation_id=result["conversation_id"],
            message=result["message"],
            task_operations=result["task_operations"],
            timestamp=result["timestamp"]
        )

    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your request"
        )
