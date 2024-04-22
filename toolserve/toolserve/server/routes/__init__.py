from fastapi import APIRouter
from toolserve.server.core.conf import settings
from toolserve.server.routes.action import router as action_router

v1 = APIRouter(prefix=settings.API_V1_STR)
v1.include_router(action_router, tags=["action"])
