from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import get_db
from models.topic import Topic
from models.user import User
from schemas.topic import TopicCreate, TopicUpdate, TopicResponse
from api.deps import get_current_user, get_current_admin

router = APIRouter(prefix="/topics", tags=["Topics"])


@router.get("/", response_model=list[TopicResponse])
async def get_topics(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    result = await db.execute(select(Topic))
    return result.scalars().all()


@router.get("/{topic_id}", response_model=TopicResponse)
async def get_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user)
):
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    return topic


@router.post("/", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
async def create_topic(
    topic_in: TopicCreate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    topic = Topic(**topic_in.model_dump())
    db.add(topic)
    await db.commit()
    await db.refresh(topic)
    return topic


@router.patch("/{topic_id}", response_model=TopicResponse)
async def update_topic(
    topic_id: int,
    topic_in: TopicUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")

    for field, value in topic_in.model_dump(exclude_unset=True).items():
        setattr(topic, field, value)

    await db.commit()
    await db.refresh(topic)
    return topic


@router.delete("/{topic_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_topic(
    topic_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    topic = await db.get(Topic, topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Тема не найдена")
    await db.delete(topic)
    await db.commit()