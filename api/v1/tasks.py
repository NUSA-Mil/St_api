from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from models.task import Task
from models.user import User
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskCheckRequest, TaskCheckResponse
from api.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("/", response_model=list[TaskResponse])
async def get_tasks(
        topic_id: Optional[int] = Query(None, description="Фильтр по ID темы"),
        db: AsyncSession = Depends(get_db),
        _user: User = Depends(get_current_user)
):
    stmt = select(Task)

    if topic_id is not None:
        stmt = stmt.where(Task.topic_id == topic_id)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
        _user: User = Depends(get_current_user)
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    return task


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
        task_in: TaskCreate,
        db: AsyncSession = Depends(get_db),
        _admin: User = Depends(get_current_admin)
):
    task = Task(**task_in.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int,
        task_in: TaskUpdate,
        db: AsyncSession = Depends(get_db),
        _admin: User = Depends(get_current_admin)
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    for field, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
        _admin: User = Depends(get_current_admin)
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")
    await db.delete(task)
    await db.commit()


@router.post("/{task_id}/check", response_model=TaskCheckResponse)
async def check_task_answer(
        task_id: int,
        payload: TaskCheckRequest,
        db: AsyncSession = Depends(get_db),
        _user: User = Depends(get_current_user)
):
    task = await db.get(Task, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Задание не найдено")

    user_ans = str(payload.user_answer).strip().lower()
    correct_ans = str(task.correct_answers).strip().lower()

    is_correct = user_ans == correct_ans

    explanation_text: str | None = str(task.explanation) if task.explanation is not None else None

    return TaskCheckResponse(
        is_correct=is_correct,
        message="Верно" if is_correct else "Неверный ответ",
        explanation=explanation_text
    )