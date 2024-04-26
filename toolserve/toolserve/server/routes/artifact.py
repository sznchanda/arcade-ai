
from typing import Annotated
from fastapi import APIRouter, Path, Query
from toolserve.server.schemas.artifact import (
    ArtifactSchemaBase,
    CreateArtifactParam,
    DeleteArtifactParam,
    GetArtifactDetails
)
from toolserve.server.services.artifact_service import artifact_service
from toolserve.server.common.response import ResponseModel, response_base
from toolserve.server.common.serializers import select_as_dict

router = APIRouter()

# Get artifact details by artifact id
@router.get('/{pk}', summary='Get artifact details')
async def get_artifact(
    pk: Annotated[int, Path(...)],
) -> ResponseModel:
    artifact = await artifact_service.get(pk=pk)
    data = GetArtifactDetails(**await select_as_dict(artifact))
    return await response_base.success(data=data)

# Create a new artifact
@router.post('', summary='Create artifact')
async def create_artifact(
    obj: CreateArtifactParam
) -> ResponseModel:
    await artifact_service.create(obj=obj)
    return await response_base.success()

# Delete artifact
@router.delete('', summary='Delete artifact')
async def delete_artifact(pk: Annotated[list[int], Query(...)]) -> ResponseModel:
    count = await artifact_service.delete(pk=pk)
    if count > 0:
        return await response_base.success()
    return await response_base.fail()

# Get all artifacts
@router.get('', summary='Get all artifacts')
async def get_all_artifacts() -> ResponseModel:
    data = await artifact_service.get_all_artifacts()
    return await response_base.success(data=data)
