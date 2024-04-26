from typing import Sequence

from sqlalchemy import Select, and_, delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from toolserve.server.crud.base import CRUDBase
from toolserve.server.models.sys_log import Log
from toolserve.server.schemas.log import CreateLog, LogSchemaBase


class CRUDLog(CRUDBase[Log, CreateLog, LogSchemaBase]):
    async def get(self, db: AsyncSession, pk: int) -> Log | None:
        return await self.get_(db, pk=pk)

    async def get_list(self, level: str = None, msg: str = None) -> Select:
        query = select(self.model).order_by(desc(self.model.created_time))
        conditions = []
        if level:
            conditions.append(self.model.level == level)
        if msg:
            conditions.append(self.model.msg.like(f'%{msg}%'))
        if conditions:
            query = query.where(and_(*conditions))
        return query

    async def get_all(self, db: AsyncSession) -> Sequence[Log]:
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def get_by_level(self, db: AsyncSession, level: str) -> Log | None:
        result = await db.execute(select(self.model).where(self.model.level == level))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: CreateLog) -> None:
        await self.create_(db, obj_in)

    async def update(self, db: AsyncSession, pk: int, obj_in: LogSchemaBase) -> int:
        return await self.update_(db, pk, obj_in)

    async def delete(self, db: AsyncSession, pk: list[int]) -> int:
        result = await db.execute(delete(self.model).where(self.model.id.in_(pk)))
        return result.rowcount


log_dao: CRUDLog = CRUDLog(Log)
