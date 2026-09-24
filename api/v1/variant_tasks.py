from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.variant_task import VariantTask
from models.user import User
from schemas.variant_task import VariantTaskCreate, VariantTaskUpdate, VariantTaskResponse
from api.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/variant-tasks", tags=["Variant Tasks"])


@router.get("", response_model=list[VariantTaskResponse])
@router.get("/", response_model=list[VariantTaskResponse])
async def get_variant_tasks(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    result = await db.execute(select(VariantTask))
    return result.scalars().all()


@router.get("/{variant_id}/{task_id}", response_model=VariantTaskResponse)
async def get_variant_task(
    variant_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    variant_task = await db.get(VariantTask, (variant_id, task_id))
    if not variant_task:
        raise HTTPException(status_code=404, detail="Связь задания и варианта не найдена")
    return variant_task


@router.post("", response_model=VariantTaskResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=VariantTaskResponse, status_code=status.HTTP_201_CREATED)
async def create_variant_task(
    vt_in: VariantTaskCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    variant_task = VariantTask(**vt_in.model_dump())
    db.add(variant_task)
    await db.commit()
    await db.refresh(variant_task)
    return variant_task


@router.patch("/{variant_id}/{task_id}", response_model=VariantTaskResponse)
async def update_variant_task(
    variant_id: int,
    task_id: int,
    vt_in: VariantTaskUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    variant_task = await db.get(VariantTask, (variant_id, task_id))
    if not variant_task:
        raise HTTPException(status_code=404, detail="Связь задания и варианта не найдена")

    for field, value in vt_in.model_dump(exclude_unset=True).items():
        setattr(variant_task, field, value)

    await db.commit()
    await db.refresh(variant_task)
    return variant_task


@router.delete("/{variant_id}/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_variant_task(
    variant_id: int,
    task_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    variant_task = await db.get(VariantTask, (variant_id, task_id))
    if not variant_task:
        raise HTTPException(status_code=404, detail="Связь задания и варианта не найдена")
    await db.delete(variant_task)
    await db.commit()