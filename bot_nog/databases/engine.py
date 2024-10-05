import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy import text

from databases.models import Base
from databases.orm_query import orm_add_banner
from commands.text_for_level import description_for_info_level



engine = create_async_engine(os.getenv('DB_LITE'), echo=True)  # создаётся асинхронное соединение с БД

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # создаются ВСЕ таблицы прописаные models.py
    async with session_maker() as session:
        #добовляем колонки name и description в таблицу с банарами, чтобы удобней было добовлять по описанию
        #в принципе нужно только в первый раз или при изменениии уровней меню
        await orm_add_banner(session=session, data=description_for_info_level) 

        

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

