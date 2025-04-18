from backend.api.gcp import api_router as gcp_router
from backend.api.azure import api_router as azure_router
from backend.api.common import api_router as common_router
from fastapi import APIRouter, Request


api_router = APIRouter()

@api_router.get("/")
def health_check(req: Request):
    return {"Success": True}


api_router.include_router(prefix="/gcp", router=gcp_router)
api_router.include_router(prefix="/azure", router=azure_router)
api_router.include_router(prefix="/common", router=common_router)

