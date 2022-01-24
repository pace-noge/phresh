from fastapi import APIRouter, Path, Body, Depends, HTTPException
from starlette import status

from app.api.dependencies.auth import get_current_active_user
from app.api.dependencies.database import get_repository
from app.db.repositories.profiles import ProfilesRepository
from app.models.profile import ProfileUpdate, ProfilePublic
from app.models.user import UserInDB

router = APIRouter()


@router.get("/{username}/", response_model=ProfilePublic, name="profiles:get-profile-by-username")
async def get_profile_by_username(
        *, username: str = Path(..., min_length=3, regex="^[a-zA-Z0-9-_]+$"),
        current_user: UserInDB = Depends(get_current_active_user),
        repo: ProfilesRepository = Depends(get_repository(ProfilesRepository))
) -> ProfilePublic:
    profile = await repo.get_profile_by_username(username=username)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No profile found with that username")
    return profile


@router.put("/me/", response_model=ProfilePublic, name="profiles:update-own-profile")
async def update_own_profile(profile_update: ProfileUpdate = Body(...)) -> ProfilePublic:
    return None