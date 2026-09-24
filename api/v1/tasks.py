from typing import Optional, Any
import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from models.task import Task, AnswerType
from models.user import User
from schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskCheckRequest, TaskCheckResponse
from api.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def normalize_val(val: Any) -> str:
    """Приводит значение к нижнему регистру и нормализует аналогичные символы."""
    if val is None:
        return ""
    s = str(val).strip().lower()
    # Заменяем английские аналоги на русские для исключения ошибок раскладки
    replacements = {'a': 'а', 'b': 'б', 'v': 'в', 'c': 'с'}
    for eng, rus in replacements.items():
        s = s.replace(eng, rus)
    return s


def compare_answers(user_ans: Any, correct_ans: Any, answer_type: AnswerType) -> bool:
    if user_ans is None or correct_ans is None:
        return False

    # Декодируем из JSON-строк при необходимости
    if isinstance(correct_ans, str):
        try:
            correct_ans = json.loads(correct_ans)
        except Exception:
            pass

    if isinstance(user_ans, str):
        try:
            user_ans = json.loads(user_ans)
        except Exception:
            pass

    # 1. Одиночный выбор (Single)
    if answer_type == AnswerType.SINGLE:
        if isinstance(correct_ans, list) and len(correct_ans) > 0:
            target = normalize_val(correct_ans[0])
        else:
            target = normalize_val(correct_ans)

        if isinstance(user_ans, list) and len(user_ans) > 0:
            user_val = normalize_val(user_ans[0])
        else:
            user_val = normalize_val(user_ans)

        return user_val == target

    # 2. Множественный выбор (Multiple)
    elif answer_type == AnswerType.MULTIPLE:
        if isinstance(user_ans, str):
            user_list = [normalize_val(x) for x in user_ans.replace(',', ' ').split() if x.strip()]
        elif isinstance(user_ans, list):
            user_list = [normalize_val(x) for x in user_ans]
        else:
            user_list = [normalize_val(user_ans)]

        if isinstance(correct_ans, list):
            correct_list = [normalize_val(x) for x in correct_ans]
        else:
            correct_list = [normalize_val(correct_ans)]

        return set(user_list) == set(correct_list)

    # 3. Сопоставление (Matching)
    elif answer_type == AnswerType.MATCHING:
        if isinstance(user_ans, dict) and isinstance(correct_ans, dict):
            u_dict = {normalize_val(k): normalize_val(v) for k, v in user_ans.items()}
            c_dict = {normalize_val(k): normalize_val(v) for k, v in correct_ans.items()}
            return u_dict == c_dict

    return normalize_val(user_ans) == normalize_val(correct_ans)


@router.get("", response_model=list[TaskResponse])
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


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
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

    is_correct = compare_answers(payload.user_answer, task.correct_answers, task.answer_type)
    explanation_text = str(task.explanation) if task.explanation is not None else None

    return TaskCheckResponse(
        is_correct=is_correct,
        correct_answers=task.correct_answers,
        message="Верно" if is_correct else "Неверный ответ",
        explanation=explanation_text
    )