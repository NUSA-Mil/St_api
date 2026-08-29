from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from core.security import get_password_hash
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse
from api.deps import get_current_admin

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
async def get_users(
        db: AsyncSession = Depends(get_db),
        _admin: User = Depends(get_current_admin)
):
    result = await db.execute(select(User))
    return result.scalars().all()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        _admin: User = Depends(get_current_admin)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_in: UserCreate,
        db: AsyncSession = Depends(get_db),
        _admin: User = Depends(get_current_admin)
):
    result = await db.execute(select(User).where(User.email == str(user_in.email)))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Пользователь с таким email уже существует")

    user = User(
        email=str(user_in.email),
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
        user_id: int,
        user_in: UserUpdate,
        db: AsyncSession = Depends(get_db),
        _admin: User = Depends(get_current_admin)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    update_data = user_in.model_dump(exclude_unset=True)
    if "email" in update_data and update_data["email"] is not None:
        update_data["email"] = str(update_data["email"])

    if "password" in update_data:
        raw_password = update_data.pop("password")
        if raw_password:
            user.hashed_password = get_password_hash(raw_password)

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
        user_id: int,
        db: AsyncSession = Depends(get_db),
        _admin: User = Depends(get_current_admin)
):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    await db.delete(user)
    await db.commit()