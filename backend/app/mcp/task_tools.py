from typing import List, Optional
from sqlmodel import select, update, delete
from sqlmodel.ext.asyncio.session import AsyncSession
from ..models.task import Task
from ..models.user import User
from ..models.message import Message
from ..models.conversation import Conversation
from datetime import datetime
import json


class TaskTools:
    """
    MCP tools for task operations that enforce user isolation and are stateless.
    """

    @staticmethod
    async def add_task(session: AsyncSession, user_id: str, title: str, description: Optional[str] = None, due_date: Optional[datetime] = None) -> dict:
        """
        Add a new task for the user.

        Args:
            session: Database session
            user_id: ID of the user creating the task
            title: Task title
            description: Optional task description
            due_date: Optional due date

        Returns:
            Dictionary with task details
        """
        task = Task(
            title=title,
            description=description,
            due_date=due_date,
            completed=False,
            user_id=user_id
        )
        session.add(task)
        await session.commit()
        await session.refresh(task)

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed": task.completed,
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }

    @staticmethod
    async def list_tasks(session: AsyncSession, user_id: str, status: Optional[str] = None, limit: Optional[int] = None) -> List[dict]:
        """
        List tasks for the user with optional filtering.

        Args:
            session: Database session
            user_id: ID of the user whose tasks to list
            status: Optional filter ('completed', 'pending', 'all')
            limit: Optional limit on number of results

        Returns:
            List of task dictionaries
        """
        query = select(Task).where(Task.user_id == user_id)

        if status == "completed":
            query = query.where(Task.completed == True)
        elif status == "pending":
            query = query.where(Task.completed == False)

        if limit:
            query = query.limit(limit)

        result = await session.exec(query)
        tasks = result.all()

        return [
            {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "completed": task.completed,
                "user_id": task.user_id,
                "created_at": task.created_at.isoformat() if task.created_at else None,
                "updated_at": task.updated_at.isoformat() if task.updated_at else None
            }
            for task in tasks
        ]

    @staticmethod
    async def update_task(session: AsyncSession, user_id: str, task_id: str, title: Optional[str] = None,
                         description: Optional[str] = None, due_date: Optional[datetime] = None,
                         completed: Optional[bool] = None) -> Optional[dict]:
        """
        Update an existing task for the user.

        Args:
            session: Database session
            user_id: ID of the user (to verify ownership)
            task_id: ID of the task to update
            title: New title (optional)
            description: New description (optional)
            due_date: New due date (optional)
            completed: New completion status (optional)

        Returns:
            Updated task dictionary or None if not found
        """
        # First verify the task belongs to the user
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.exec(stmt)
        task = result.first()

        if not task:
            return None

        # Update fields that were provided
        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if due_date is not None:
            task.due_date = due_date
        if completed is not None:
            task.completed = completed

        task.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(task)

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed": task.completed,
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }

    @staticmethod
    async def complete_task(session: AsyncSession, user_id: str, task_id: str) -> Optional[dict]:
        """
        Mark a task as completed for the user.

        Args:
            session: Database session
            user_id: ID of the user (to verify ownership)
            task_id: ID of the task to complete

        Returns:
            Updated task dictionary or None if not found
        """
        stmt = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.exec(stmt)
        task = result.first()

        if not task:
            return None

        task.completed = True
        task.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(task)

        return {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed": task.completed,
            "user_id": task.user_id,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }

    @staticmethod
    async def delete_task(session: AsyncSession, user_id: str, task_id: str) -> bool:
        """
        Delete a task for the user.

        Args:
            session: Database session
            user_id: ID of the user (to verify ownership)
            task_id: ID of the task to delete

        Returns:
            True if deleted, False if not found
        """
        stmt = delete(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.exec(stmt)

        await session.commit()

        # Check if any row was affected
        return result.rowcount > 0