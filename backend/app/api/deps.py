from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated
from typing import Tuple
from ..db import get_async_session
from ..core.security import verify_jwt

security = HTTPBearer(auto_error=True)

async def get_current_user(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> str:
    payload = verify_jwt(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user information",
        )

    return user_id

async def get_current_user_with_email(
    token: Annotated[HTTPAuthorizationCredentials, Depends(security)]
) -> Tuple[str, str]:
    """
    Extract both user ID and email from JWT token.
    Returns a tuple of (user_id, email).
    """
    payload = verify_jwt(token.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )

    # Try different possible field names for user ID (Better Auth might use different claims)
    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
    email = payload.get("email") or payload.get("user_email", f"{user_id or 'unknown'}@example.com")  # Fallback if email not in token

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user information",
        )

    return str(user_id), str(email)

# Chat-specific dependency that validates user_id parameter matches authenticated user
async def validate_user_ownership(
    user_id: str,
    current_user_id: Annotated[str, Depends(get_current_user)]
) -> str:
    """
    Validates that the user_id in the path matches the authenticated user's ID.
    This ensures users can only access their own data.
    """
    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own data",
        )
    return current_user_id

# Chat-specific dependency that validates user and returns both user_id and email
async def validate_chat_user_access(
    user_id: str,
    current_user_data: Annotated[Tuple[str, str], Depends(get_current_user_with_email)]
) -> Tuple[str, str]:
    """
    Validates that the user_id in the path matches the authenticated user's ID
    and returns both user_id and email for chat operations.
    """
    current_user_id, email = current_user_data

    if user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own data",
        )
    return current_user_id, email

# Type alias for cleaner route dependencies
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]
CurrentUserDep = Annotated[str, Depends(get_current_user)]
UserIdValidationDep = Annotated[str, Depends(validate_user_ownership)]
ChatUserValidationDep = Annotated[Tuple[str, str], Depends(validate_chat_user_access)]
