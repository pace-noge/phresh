from typing import List
from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def get_all_cleanings() -> List[dict]:
    cleanings = [
        {"id": 1, "name": "My House", "cleaning_type": "full_clean", "price_per_hour": 29.99}
    ]
    return cleanings
