from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from core.config import settings


# Создаем асинхронный движок для PostgreSQL
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,          # Установи True, если нужно видеть SQL-запросы в консоли
    future=True,
    pool_pre_ping=True  # Проверка живого соединения перед запросом
)

# Фабрика асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)


# Базовый класс для всех моделей SQLAlchemy
class Base(DeclarativeBase):
    pass


# Зависимость (Dependency) для получения сессии БД в FastAPI эндпоинтах
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()