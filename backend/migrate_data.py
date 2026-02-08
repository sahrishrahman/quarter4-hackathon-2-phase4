#!/usr/bin/env python3
"""
Data Migration Script
Migrates data from local SQLite database to Neon PostgreSQL database
"""

import asyncio
import sqlite3
import sys
from datetime import datetime
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession as SQLAlchemyAsyncSession
from app.models.user import User
from app.models.task import Task
from app.models.conversation import Conversation
from app.models.message import Message
from app.core.config import settings
import asyncpg
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse


async def migrate_users(sqlite_conn, async_session: AsyncSession):
    """Migrate users from SQLite to PostgreSQL"""
    print("Starting user migration...")

    # Get users from SQLite
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("""
        SELECT id, email, name, hashed_password, created_at, updated_at
        FROM user
    """)
    sqlite_users = sqlite_cursor.fetchall()

    migrated_count = 0
    for user_row in sqlite_users:
        user_id, email, name, hashed_password, created_at, updated_at = user_row

        # Check if user already exists in PostgreSQL
        existing_user = await async_session.exec(select(User).where(User.id == user_id))
        existing_user = existing_user.first()

        if not existing_user:
            # Create new user in PostgreSQL
            pg_user = User(
                id=user_id,
                email=email,
                name=name,
                hashed_password=hashed_password,
                created_at=datetime.fromisoformat(created_at) if created_at else datetime.utcnow(),
                updated_at=datetime.fromisoformat(updated_at) if updated_at else datetime.utcnow()
            )

            async_session.add(pg_user)
            print(f"Migrated user: {email}")
            migrated_count += 1
        else:
            print(f"User already exists: {email}")

    await async_session.commit()
    print(f"Completed user migration. Migrated {migrated_count} users.")
    return migrated_count


async def migrate_tasks(sqlite_conn, async_session: AsyncSession):
    """Migrate tasks from SQLite to PostgreSQL"""
    print("Starting task migration...")

    # Get tasks from SQLite
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("""
        SELECT id, title, description, completed, created_at, updated_at, user_id
        FROM task
    """)
    sqlite_tasks = sqlite_cursor.fetchall()

    migrated_count = 0
    for task_row in sqlite_tasks:
        task_id, title, description, completed, created_at, updated_at, user_id = task_row

        # Check if task already exists in PostgreSQL
        existing_task = await async_session.exec(select(Task).where(Task.id == task_id))
        existing_task = existing_task.first()

        if not existing_task:
            # Create new task in PostgreSQL
            pg_task = Task(
                id=task_id,
                title=title,
                description=description or "",
                completed=bool(completed),
                created_at=datetime.fromisoformat(created_at) if created_at else None,
                updated_at=datetime.fromisoformat(updated_at) if updated_at else None,
                user_id=user_id
            )

            async_session.add(pg_task)
            print(f"Migrated task: {title}")
            migrated_count += 1
        else:
            print(f"Task already exists: {title}")

    await async_session.commit()
    print(f"Completed task migration. Migrated {migrated_count} tasks.")
    return migrated_count


async def migrate_conversations(sqlite_conn, async_session: AsyncSession):
    """Migrate conversations from SQLite to PostgreSQL"""
    print("Starting conversation migration...")

    # Get conversations from SQLite
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("""
        SELECT id, title, user_id, is_active, created_at, updated_at
        FROM conversation
    """)
    sqlite_conversations = sqlite_cursor.fetchall()

    migrated_count = 0
    for conv_row in sqlite_conversations:
        conv_id, title, user_id, is_active, created_at, updated_at = conv_row

        # Check if conversation already exists in PostgreSQL
        existing_conv = await async_session.exec(select(Conversation).where(Conversation.id == conv_id))
        existing_conv = existing_conv.first()

        if not existing_conv:
            # Create new conversation in PostgreSQL
            pg_conv = Conversation(
                id=conv_id,
                title=title,
                user_id=user_id,
                is_active=bool(is_active),
                created_at=datetime.fromisoformat(created_at) if created_at else None,
                updated_at=datetime.fromisoformat(updated_at) if updated_at else None
            )

            async_session.add(pg_conv)
            print(f"Migrated conversation: {title}")
            migrated_count += 1
        else:
            print(f"Conversation already exists: {title}")

    await async_session.commit()
    print(f"Completed conversation migration. Migrated {migrated_count} conversations.")
    return migrated_count


async def migrate_messages(sqlite_conn, async_session: AsyncSession):
    """Migrate messages from SQLite to PostgreSQL"""
    print("Starting message migration...")

    # Get messages from SQLite
    sqlite_cursor = sqlite_conn.cursor()
    sqlite_cursor.execute("""
        SELECT id, conversation_id, user_id, role, content, message_metadata, timestamp
        FROM message
    """)
    sqlite_messages = sqlite_cursor.fetchall()

    migrated_count = 0
    for msg_row in sqlite_messages:
        msg_id, conv_id, user_id, role, content, metadata, timestamp = msg_row

        # Check if message already exists in PostgreSQL
        existing_msg = await async_session.exec(select(Message).where(Message.id == msg_id))
        existing_msg = existing_msg.first()

        if not existing_msg:
            # Create new message in PostgreSQL
            pg_msg = Message(
                id=msg_id,
                conversation_id=conv_id,
                user_id=user_id,
                role=role,
                content=content,
                message_metadata=metadata,
                timestamp=datetime.fromisoformat(timestamp) if timestamp else None
            )

            async_session.add(pg_msg)
            print(f"Migrated message: {role} - {content[:30]}...")
            migrated_count += 1
        else:
            print(f"Message already exists: {role} - {content[:30]}...")

    await async_session.commit()
    print(f"Completed message migration. Migrated {migrated_count} messages.")
    return migrated_count


async def main():
    print("Starting data migration from SQLite to PostgreSQL...")

    # Connect to SQLite database
    sqlite_conn = sqlite3.connect('todo_dev.db')

    try:
        # Process the PostgreSQL connection URL
        database_url = settings.DATABASE_URL

        if database_url.startswith("postgresql://"):
            # Convert to asyncpg format for PostgreSQL
            database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

            # Clean up query params for asyncpg
            from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
            parsed = urlparse(database_url)
            qs = parse_qs(parsed.query)

            # Remove unsupported keys
            for key in ["sslmode", "channel_binding", "options"]:
                qs.pop(key, None)

            # Rebuild URL without forcing ssl query params; we'll pass SSL via connect_args
            new_query = urlencode(qs, doseq=True)
            database_url = urlunparse(parsed._replace(query=new_query))

            # Determine connect args: enable SSL for non-local hosts (e.g., Neon)
            connect_args = {}
            hostname = parsed.hostname or ""
            if hostname not in ("localhost", "127.0.0.1", ""):
                # asyncpg expects `ssl` argument (True or SSLContext) instead of sslmode
                connect_args = {"ssl": True}
            else:
                connect_args = {}
        else:
            # For other database types, use default connect_args
            parsed = urlparse(database_url)
            hostname = parsed.hostname or ""
            if hostname not in ("localhost", "127.0.0.1", ""):
                connect_args = {"ssl": True}
            else:
                connect_args = {}

        # Connect to PostgreSQL database
        engine = create_async_engine(
            database_url,
            echo=True,
            connect_args=connect_args,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=10,
            max_overflow=20
        )

        async with AsyncSession(engine) as session:
            # Migrate data in the correct order (users first, then tasks, etc.)
            users_migrated = await migrate_users(sqlite_conn, session)
            tasks_migrated = await migrate_tasks(sqlite_conn, session)
            conversations_migrated = await migrate_conversations(sqlite_conn, session)
            messages_migrated = await migrate_messages(sqlite_conn, session)

            print(f"\nMigration completed successfully!")
            print(f"- Users: {users_migrated} migrated")
            print(f"- Tasks: {tasks_migrated} migrated")
            print(f"- Conversations: {conversations_migrated} migrated")
            print(f"- Messages: {messages_migrated} migrated")

    finally:
        sqlite_conn.close()


if __name__ == "__main__":
    asyncio.run(main())