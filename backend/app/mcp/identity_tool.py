from typing import Dict, Any
from sqlmodel.ext.asyncio.session import AsyncSession


class IdentityTool:
    """
    MCP tool for getting current user identity from JWT.
    """

    @staticmethod
    async def get_current_user(user_id: str, email: str) -> Dict[str, Any]:
        """
        Get current user identity information.

        Args:
            user_id: The authenticated user ID from JWT
            email: The authenticated user email from JWT

        Returns:
            Dictionary with user identity information
        """
        return {
            "email": email,
            "user_id": user_id
        }