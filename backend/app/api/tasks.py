from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select
from typing import List, Optional
from ..models.task import Task, TaskCreate, TaskUpdate
from .deps import SessionDep, CurrentUserDep

from fastapi import APIRouter, HTTPException, Query, status
from sqlmodel import select
from typing import List, Optional
from ..models.task import Task, TaskCreate, TaskUpdate
from .deps import SessionDep, CurrentUserDep

router = APIRouter()

@router.get("/", response_model=List[Task])
async def list_tasks(
    current_user: CurrentUserDep,
    session: SessionDep,
    status: Optional[str] = Query(None, pattern="^(all|pending|completed)$")
):
    query = select(Task).where(Task.user_id == current_user)

    if status == "pending":
        query = query.where(Task.completed == False)
    elif status == "completed":
        query = query.where(Task.completed == True)

    results = await session.execute(query)
    return results.scalars().all()

@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
async def create_task(
    current_user: CurrentUserDep,
    task_in: TaskCreate,
    session: SessionDep
):
    task = Task(**task_in.model_dump(), user_id=current_user)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.get("/{id}", response_model=Task)
async def get_task(
    id: int,
    current_user: CurrentUserDep,
    session: SessionDep
):
    task = await session.get(Task, id)
    if not task or task.user_id != current_user:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{id}", response_model=Task)
async def update_task(
    id: int,
    current_user: CurrentUserDep,
    task_in: TaskUpdate,
    session: SessionDep
):
    task = await session.get(Task, id)
    if not task or task.user_id != current_user:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)

    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    id: int,
    current_user: CurrentUserDep,
    session: SessionDep
):
    task = await session.get(Task, id)
    if not task or task.user_id != current_user:
        raise HTTPException(status_code=404, detail="Task not found")

    await session.delete(task)
    await session.commit()
    return None

@router.patch("/{id}/complete", response_model=Task)
async def toggle_complete(
    id: int,
    current_user: CurrentUserDep,
    session: SessionDep
):
    task = await session.get(Task, id)
    if not task or task.user_id != current_user:
        raise HTTPException(status_code=404, detail="Task not found")

    task.completed = not task.completed
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task
