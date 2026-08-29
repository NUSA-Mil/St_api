from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from core.database import get_db
from models.exam_variant import ExamVariant
from models.variant_task import VariantTask
from models.user import User
from schemas.exam_variant import (
    ExamVariantCreate,
    ExamVariantUpdate,
    ExamVariantResponse,
    TaskWithOrderResponse,
    SubmitExamRequest,
    SubmitExamResponse,
    TaskCheckResult
)
from api.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/exam-variants", tags=["Exam Variants"])


@router.get("/", response_model=list[ExamVariantResponse])
async def get_exam_variants(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    result = await db.execute(select(ExamVariant))
    return result.scalars().all()


@router.get("/{variant_id}", response_model=ExamVariantResponse)
async def get_exam_variant(
    variant_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    variant = await db.get(ExamVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Вариант экзамена не найден")
    return variant


@router.get("/{variant_id}/tasks", response_model=list[TaskWithOrderResponse])
async def get_exam_variant_tasks(
    variant_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    """Получает все задания варианта, отсортированные по 'order'."""
    variant = await db.get(ExamVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Вариант экзамена не найден")

    stmt = (
        select(VariantTask)
        .where(VariantTask.variant_id == variant_id)
        .options(selectinload(VariantTask.task))
        .order_by(VariantTask.order)
    )
    result = await db.execute(stmt)
    variant_tasks = result.scalars().all()

    response_tasks = []
    for vt in variant_tasks:
        task_dict = vt.task.__dict__.copy()
        task_dict["order"] = vt.order
        response_tasks.append(TaskWithOrderResponse.model_validate(task_dict))

    return response_tasks


@router.post("/{variant_id}/submit", response_model=SubmitExamResponse)
async def submit_exam_variant(
    variant_id: int,
    payload: SubmitExamRequest,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    """Проверяет ответы пользователя по всему варианту и возвращает подробную статистику."""
    variant = await db.get(ExamVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Вариант экзамена не найден")

    stmt = (
        select(VariantTask)
        .where(VariantTask.variant_id == variant_id)
        .options(selectinload(VariantTask.task))
    )
    result = await db.execute(stmt)
    variant_tasks = result.scalars().all()

    if not variant_tasks:
        raise HTTPException(status_code=400, detail="В этом варианте нет заданий")

    # Преобразуем входящие ответы пользователя в словарь {task_id: user_answer}
    user_answers_map = {item.task_id: item.user_answer for item in payload.answers}

    results: list[TaskCheckResult] = []
    correct_count = 0

    for vt in variant_tasks:
        task = vt.task
        user_ans = user_answers_map.get(task.id)

        if user_ans is not None:
            formatted_user_ans = str(user_ans).strip().lower()
            formatted_correct_ans = str(task.correct_answers).strip().lower()
            is_correct = formatted_user_ans == formatted_correct_ans
        else:
            is_correct = False

        if is_correct:
            correct_count += 1

        explanation_text: str | None = str(task.explanation) if task.explanation is not None else None

        results.append(
            TaskCheckResult(
                task_id=task.id,
                user_answer=user_ans,
                is_correct=is_correct,
                correct_answers=task.correct_answers,
                explanation=explanation_text
            )
        )

    total_tasks = len(variant_tasks)
    score_percentage = round((correct_count / total_tasks) * 100, 2)

    return SubmitExamResponse(
        variant_id=variant_id,
        total_tasks=total_tasks,
        correct_count=correct_count,
        score_percentage=score_percentage,
        results=results
    )


@router.post("/", response_model=ExamVariantResponse, status_code=status.HTTP_201_CREATED)
async def create_exam_variant(
    variant_in: ExamVariantCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    variant = ExamVariant(**variant_in.model_dump())
    db.add(variant)
    await db.commit()
    await db.refresh(variant)
    return variant


@router.patch("/{variant_id}", response_model=ExamVariantResponse)
async def update_exam_variant(
    variant_id: int,
    variant_in: ExamVariantUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    variant = await db.get(ExamVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Вариант экзамена не найден")

    for field, value in variant_in.model_dump(exclude_unset=True).items():
        setattr(variant, field, value)

    await db.commit()
    await db.refresh(variant)
    return variant


@router.delete("/{variant_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exam_variant(
    variant_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    variant = await db.get(ExamVariant, variant_id)
    if not variant:
        raise HTTPException(status_code=404, detail="Вариант экзамена не найден")
    await db.delete(variant)
    await db.commit()