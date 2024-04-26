
from typing import Sequence

from sqlalchemy import Select

from toolserve.server.common.exception import errors
from toolserve.server.crud.crud_log import log_dao
from toolserve.server.database.db_sqlite import async_db_session
from toolserve.server.models.sys_log import Log
from toolserve.server.schemas.log import CreateLog, LogSchemaBase


class LogService:
    @staticmethod
    async def get(*, pk: int) -> Log:
        async with async_db_session() as db:
            log = await log_dao.get(db, pk)
            if not log:
                raise errors.NotFoundError(msg='Log entry not found')
            return log


    @staticmethod
    async def get_log_list() -> Sequence[Log]:
        async with async_db_session() as db:
            logs = await log_dao.get_all(db)
            return logs

    @staticmethod
    async def create(*, obj: CreateLog) -> None:
        async with async_db_session.begin() as db:
            await log_dao.create(db, obj)

    @staticmethod
    async def update(*, pk: int, obj: LogSchemaBase) -> int:
        async with async_db_session.begin() as db:
            count = await log_dao.update(db, pk, obj)
            return count

    @staticmethod
    async def delete(*, pk: list[int]) -> int:
        async with async_db_session.begin() as db:
            count = await log_dao.delete(db, pk)
            return count


log_service: LogService = LogService()
