from typing import List
from fastapi import APIRouter, Body, Depends, HTTPException, Path
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.cleanings import get_cleaning_by_id_from_path, check_cleaning_modification_permissions
from app.models.cleaning import CleaningCreate, CleaningPublic, CleaningInDB, CleaningUpdate
from app.db.repositories.cleanings import CleaningsRepository
from app.api.dependencies.database import get_repository
from app.models.user import UserInDB

router = APIRouter()


@router.get("/", response_model=List[CleaningPublic], name="cleanings:list-all-user-cleanings")
async def list_all_user_cleanings(
        current_user: UserInDB = Depends(get_current_active_user),
        repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))
) -> List[CleaningPublic]:
    return await repo.list_all_user_cleanings(requesting_user=current_user)


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


@router.get("/", response_model=List[CleaningPublic], name="cleanings:get-all-cleanings")
async def get_all_cleanings(cleanings_repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))) -> List[CleaningInDB]:
    return await cleanings_repo.get_all_cleaning()


@router.get("/{cleaning_id}/", response_model=CleaningPublic, name="cleanings:get-cleaning-by-id")
async def get_cleaning_by_id(
        cleaning: CleaningInDB = Depends(get_cleaning_by_id_from_path)
) -> CleaningPublic:
    return cleaning


@router.put(
    "/{cleaning_id}/",
    response_model=CleaningPublic,
    name="cleanings:update-cleaning-by-id",
    dependencies=[Depends(check_cleaning_modification_permissions)],
)
async def update_cleaning_by_id(
        cleaning: CleaningInDB = Depends(get_cleaning_by_id_from_path),
        cleaning_update: CleaningUpdate = Body(...),
        repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))
) -> CleaningPublic:
    return await repo.update_cleaning(cleaning=cleaning, cleaning_update=cleaning_update)


@router.delete(
    "/{cleaning_id}/",
    response_model=int,
    name="cleanings:delete-cleaning-by-id",
    dependencies=[Depends(check_cleaning_modification_permissions)]
)
async def delete_cleaning_by_id(
        cleaning: CleaningInDB = Depends(get_cleaning_by_id_from_path),
        repo: CleaningsRepository = Depends(get_repository(CleaningsRepository))
) -> None:
    return await repo.delete_cleaning_by_id(cleaning=cleaning)
