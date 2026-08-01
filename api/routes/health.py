from fastapi import APIRouter

router = APIRouter(tags=["HEALTH"])


@router.get("/health")
async def health():
    return "up"
