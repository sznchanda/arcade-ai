from typing import Sequence

from sqlalchemy import select
from toolserve.server.common.exception import errors
from toolserve.server.crud.crud_artifact import artifact_dao
from toolserve.server.database.db_sqlite import async_db_session
from toolserve.server.models.sys_artifact import Artifact
from toolserve.server.schemas.artifact import CreateArtifactParam, ArtifactSchemaBase
from toolserve.server.core.conf import settings
import os

class ArtifactService:
    @staticmethod
    async def get(*, pk: int) -> Artifact:
        async with async_db_session() as db:
            artifact = await artifact_dao.get(db, pk)
            if not artifact:
                raise errors.NotFoundError(msg='Artifact not found')
            return artifact

    @staticmethod
    async def get_all_artifacts() -> Sequence[Artifact]:
        async with async_db_session() as db:
            artifacts = await artifact_dao.get_all(db)
            return artifacts

    @staticmethod
    async def create(*, obj: CreateArtifactParam) -> None:
        async with async_db_session.begin() as db:
            artifact = Artifact(name=obj.name, file_path=os.path.join(settings.ARTIFACTS_DIR, obj.name))
            await artifact_dao.create(db, artifact)  # This line persists the artifact in the database.
            with open(artifact.file_path, 'wb') as file:
                file.write(obj.data)

    @staticmethod
    async def update(*, pk: int, obj: ArtifactSchemaBase) -> int:
        async with async_db_session.begin() as db:
            count = await artifact_dao.update(db, pk, obj)
            return count

    @staticmethod
    async def delete(*, pk: list[int]) -> int:
        async with async_db_session.begin() as db:
            count = await artifact_dao.delete(db, pk)
            return count

artifact_service: ArtifactService = ArtifactService()
