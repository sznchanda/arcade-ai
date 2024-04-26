from typing import Sequence

from sqlalchemy import select
from toolserve.server.common.exception import errors
from toolserve.server.crud.crud_data import data_dao
from toolserve.server.database.db_sqlite import async_db_session
from toolserve.server.models.sys_data import Data
from toolserve.server.schemas.data import CreateDataParam, DataSchemaBase
from toolserve.server.core.conf import settings
import os
import json

class DataService:
    @staticmethod
    async def get(*, pk: int) -> Data:
        async with async_db_session() as db:
            data = await data_dao.get(db, pk)
            if not data:
                raise errors.NotFoundError(msg='Data not found')
            return data

    @staticmethod
    async def get_all_data() -> Sequence[Data]:
        async with async_db_session() as db:
            data_entries = await data_dao.get_all(db)
            return data_entries

    @staticmethod
    async def create(*, obj: CreateDataParam) -> Data:
        async with async_db_session.begin() as db:
            file_name = obj.file_name + ".json" if not obj.file_name.endswith(".json") else obj.file_name
            obj.file_path = os.path.join(settings.DATA_DIR, file_name)

            data = obj.copy(exclude={'json_blob'})  # Save everything but the data
            db_model = await data_dao.create(db, data)  # This now returns the ID

            await db.commit()

        # TODO figure out how to save it so it doesnt overwrite the existing file
        os.makedirs(os.path.dirname(obj.file_path), exist_ok=True)
        with open(obj.file_path, 'w') as file:
            file.write(obj.json_blob)

        return db_model


    @staticmethod
    async def update(*, pk: int, obj: DataSchemaBase) -> int:
        async with async_db_session.begin() as db:
            count = await data_dao.update(db, pk, obj)
            return count

    @staticmethod
    async def delete(*, pk: list[int]) -> int:
        async with async_db_session.begin() as db:
            count = await data_dao.delete(db, pk)
            return count


data_service: DataService = DataService()
