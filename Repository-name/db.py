from sqlalchemy.orm import sessionmaker # type: ignore
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine # type: ignore
from sqlalchemy.orm import DeclarativeBase # type: ignore

from .config import config

engine = create_async_engine(url = config.env_data.DB_URl_ASYNC, echo=True)

session = sessionmaker(engine,class_=AsyncSession )

async def get_session():
    async with session() as connection:
        yield connection
        
        
class Base(DeclarativeBase):
    ...