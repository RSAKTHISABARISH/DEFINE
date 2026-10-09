from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import get_settings

settings = get_settings()

# Support both sqlite (dev) and postgresql (prod)
DB_URL = settings.DATABASE_URL
if DB_URL.startswith("postgresql+psycopg://"):
    engine = create_async_engine(DB_URL, pool_pre_ping=True, pool_size=10, max_overflow=20)
elif DB_URL.startswith("sqlite"):
    # Ensure we use aiosqlite for async sqlite
    if "sqlite+aiosqlite" not in DB_URL:
        DB_URL = DB_URL.replace("sqlite://", "sqlite+aiosqlite://")
    engine = create_async_engine(DB_URL, connect_args={"check_same_thread": False})
else:
    engine = create_async_engine(DB_URL, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
