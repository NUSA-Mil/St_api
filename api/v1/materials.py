from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from core.database import get_db
from models.material import Material
from models.topic import Topic
from models.user import User
from schemas.material import MaterialCreate, MaterialUpdate, MaterialResponse
from api.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.get("/", response_model=list[MaterialResponse])
async def get_materials(
    topic_id: Optional[int] = Query(None, description="Фильтр по ID темы"),
    subject_id: Optional[int] = Query(None, description="Фильтр по ID предмета"),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    stmt = select(Material)

    if subject_id is not None:
        stmt = stmt.join(Topic, Material.topic_id == Topic.id).where(Topic.subject_id == subject_id)

    if topic_id is not None:
        stmt = stmt.where(Material.topic_id == topic_id)

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{material_id}", response_model=MaterialResponse)
async def get_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    return material


@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED)
async def create_material(
    material_in: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    material = Material(**material_in.model_dump())
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material


@router.patch("/{material_id}", response_model=MaterialResponse)
async def update_material(
    material_id: int,
    material_in: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")

    for field, value in material_in.model_dump(exclude_unset=True).items():
        setattr(material, field, value)

    await db.commit()
    await db.refresh(material)
    return material


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    material = await db.get(Material, material_id)
    if not material:
        raise HTTPException(status_code=404, detail="Материал не найден")
    await db.delete(material)
    await db.commit()