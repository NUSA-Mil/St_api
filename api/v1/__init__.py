from fastapi import APIRouter
from api.v1.auth import router as auth_router
from api.v1.users import router as users_router
from api.v1.subjects import router as subjects_router
from api.v1.topics import router as topics_router
from api.v1.materials import router as materials_router
from api.v1.tasks import router as tasks_router
from api.v1.exam_variants import router as exam_variants_router
from api.v1.variant_tasks import router as variant_tasks_router

api_router = APIRouter(prefix="/v1")

api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(subjects_router)
api_router.include_router(topics_router)
api_router.include_router(materials_router)
api_router.include_router(tasks_router)
api_router.include_router(exam_variants_router)
api_router.include_router(variant_tasks_router)