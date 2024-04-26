#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Sequence

from sqlalchemy import Select, and_, delete, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from toolserve.server.crud.base import CRUDBase
from toolserve.server.models.sys_artifact import Artifact
from toolserve.server.schemas.artifact import CreateArtifactParam, UpdateArtifactParam


class CRUDArtifact(CRUDBase[Artifact, CreateArtifactParam, UpdateArtifactParam]):
    async def get(self, db: AsyncSession, pk: int) -> Artifact | None:
        return await self.get_(db, pk=pk)

    async def get_list(self, name: str = None, file_path: str = None) -> Select:
        se = select(self.model).order_by(desc(self.model.created_time))
        where_list = []
        if name:
            where_list.append(self.model.name.like(f'%{name}%'))
        if file_path:
            where_list.append(self.model.file_path.like(f'%{file_path}%', escape='/'))
        if where_list:
            se = se.where(and_(*where_list))
        return se

    async def get_all(self, db: AsyncSession) -> Sequence[Artifact]:
        artifacts = await db.execute(select(self.model))
        return artifacts.scalars().all()

    async def get_by_name(self, db: AsyncSession, name: str) -> Artifact | None:
        artifact = await db.execute(select(self.model).where(self.model.name == name))
        return artifact.scalars().first()

    async def create(self, db: AsyncSession, obj_in: CreateArtifactParam) -> None:
        await self.create_(db, obj_in)

    async def update(self, db: AsyncSession, pk: int, obj_in: UpdateArtifactParam) -> int:
        return await self.update_(db, pk, obj_in)

    async def delete(self, db: AsyncSession, pk: list[int]) -> int:
        artifacts = await db.execute(delete(self.model).where(self.model.id.in_(pk)))
        return artifacts.rowcount


artifact_dao: CRUDArtifact = CRUDArtifact(Artifact)
