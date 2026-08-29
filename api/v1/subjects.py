from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.subject import Subject
from models.user import User
from schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from api.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.get("/", response_model=list[SubjectResponse])
async def get_subjects(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    result = await db.execute(select(Subject))
    return result.scalars().all()


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    subject = await db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    return subject


@router.post("/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_in: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    subject = Subject(**subject_in.model_dump())
    db.add(subject)
    await db.commit()
    await db.refresh(subject)
    return subject


@router.patch("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    subject_in: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    subject = await db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Предмет не найден")

    for field, value in subject_in.model_dump(exclude_unset=True).items():
        setattr(subject, field, value)

    await db.commit()
    await db.refresh(subject)
    return subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    subject = await db.get(Subject, subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Предмет не найден")
    await db.delete(subject)
    await db.commit()