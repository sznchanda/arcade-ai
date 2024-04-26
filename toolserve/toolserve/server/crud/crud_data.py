import datetime
from typing import Sequence
from sqlalchemy import Select, and_, delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from toolserve.server.crud.base import CRUDBase
from toolserve.server.models.sys_data import Data
from toolserve.server.schemas.data import CreateDataParam, DataSchemaBase

class CRUDData(CRUDBase[Data, CreateDataParam, DataSchemaBase]):
    async def get(self, db: AsyncSession, pk: int) -> Data | None:
        return await self.get_(db, pk=pk)

    async def get_list(self, file_name: str = None, file_path: str = None) -> Select:
        query = select(self.model).order_by(desc(self.model.created_time))
        conditions = []
        if file_name:
            conditions.append(self.model.file_name.like(f'%{file_name}%'))
        if file_path:
            conditions.append(self.model.file_path.like(f'%{file_path}%'))
        if conditions:
            query = query.where(and_(*conditions))
        return query

    async def get_all(self, db: AsyncSession) -> Sequence[Data]:
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def get_by_file_name(self, db: AsyncSession, file_name: str) -> Data | None:
        result = await db.execute(select(self.model).where(self.model.file_name == file_name))
        return result.scalars().first()

    async def create(self, db: AsyncSession, obj_in: CreateDataParam) -> Data:
        existing_data = await self.get_by_file_name(db, obj_in.file_name)
        if existing_data:
            existing_data.updated_time = datetime.datetime.now()
            db.add(existing_data)
            return existing_data
        else:
            obj = self.model(**obj_in.dict())
            db.add(obj)
            return obj

    async def update(self, db: AsyncSession, pk: int, obj_in: DataSchemaBase) -> int:
        return await self.update_(db, pk, obj_in)

    async def delete(self, db: AsyncSession, pk: list[int]) -> int:
        result = await db.execute(delete(self.model).where(self.model.id.in_(pk)))
        return result.rowcount

data_dao: CRUDData = CRUDData(Data)
