from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from app.api.dependencies.auth import get_current_active_user
from app.models.cleaning import CleaningCreate, CleaningPublic, CleaningInDB, CleaningUpdate
from app.db.repositories.cleanings import CleaningsRepository
from app.api.dependencies.database import get_repository
from app.models.user import UserInDB

router = APIRouter()


@router.get("/")
async def get_all_cleanings(repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))) -> List[CleaningPublic]:
    cleanings = await repo.get_all_cleanings()
    return cleanings


@router.post("/", response_model=CleaningPublic, name="cleanings:create-cleaning", status_code=HTTP_201_CREATED)
async def create_new_cleanings(
        new_cleaning: CleaningCreate = Body(...),
        current_user: UserInDB = Depends(get_current_active_user),
        cleanings_repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))
) -> CleaningPublic:
    """
    Create new cleaning.

    :param new_cleaning: CleaningCreate object
    :param current_user: Current user request
    :param cleanings_repo: CleaningsRepository
    :return: CleaningPublic object
    """
    created_cleaning = await cleanings_repo.create_cleaning(new_cleaning=new_cleaning, requesting_user=current_user)
    return created_cleaning


@router.get("/{id}/", response_model=CleaningPublic, name="cleanings:get-cleaning-by-id")
async def get_cleaning_by_id(
        id: int,
        cleanings_repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))
) -> CleaningPublic:
    cleaning = await cleanings_repo.get_cleaning_by_id(id=id)
    if not cleaning:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="No cleaning found with that id.")
    return cleaning


@router.get("/", response_model=List[CleaningPublic], name="cleanings:get-all-cleanings")
async def get_all_cleanings(cleanings_repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))) -> List[CleaningInDB]:
    return await cleanings_repo.get_all_cleaning()


@router.put("/{id}/", response_model=CleaningPublic, name="cleanings:update-cleaning-by-id")
async def update_cleaning_by_id(
        id: int = Path(..., ge=1, title="The ID of cleaning to update"),
        cleaning_update: CleaningUpdate = Body(...),
        repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))
) -> CleaningPublic:
    update_cleaning = await repo.update_cleaning_by_id(id=id, cleaning_update=cleaning_update)
    if not update_cleaning:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail='No cleaning found with that ID.'
        )
    return update_cleaning


@router.delete("/{id}/", status_code=HTTP_204_NO_CONTENT, name="cleanings:delete-cleaning-by-id")
async def delete_cleaning_by_id(
        id: int = Path(..., ge=1, title="The ID of cleaning to delete"),
        repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))
) -> None:
    deleted = await repo.delete_cleaning_by_id(id=id)
    if deleted is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="cleaning id not found")
    return None
