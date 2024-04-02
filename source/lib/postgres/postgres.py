from logging import Logger

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncConnection
from sqlalchemy import select
from sqlalchemy import func

from lib.postgres.models import *


class Postgres:
    def __init__(self, url, logger: Logger):
        self.url = url
        self.logger = logger

        self.engine = create_async_engine(self.url, echo=False)
        self.async_session = async_sessionmaker(self.engine, class_=AsyncSession, expire_on_commit=False)

    async def get_user(self, id: int):
        async with self.async_session() as session:
            stmt = select(Users).where(Users.user_id == id)
            return await session.scalar(stmt)

    async def get_topics(self):
        async with self.async_session() as session:
            stmt = select(Topics)
            return await session.scalars(stmt)

    async def get_topic(self, id: int):
        async with self.async_session() as session:
            stmt = select(Topics).where(Topics.id == id)
            return await session.scalars(stmt)

    async def insert_object(self, orm_object: Base):
        async with self.async_session() as session:
            async with session.begin():
                session.add(orm_object)

    async def create_tables(self):
        self.logger.info('Create tables')
        async with self.engine.begin() as conn:  # type: AsyncConnection
            await conn.run_sync(Base.metadata.create_all)

    async def drop_tables(self):
        self.logger.info('Drop tables')
        async with self.engine.begin() as conn:  # type: AsyncConnection
            await conn.run_sync(Base.metadata.drop_all)
