from fastapi import APIRouter, Body, Path, Depends, HTTPException
from starlette.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND

from app.api.dependencies.database import get_repository
from app.models.user import UserCreate, UserPublic
from app.models.token import AccessToken
from app.services import auth_service

from app.db.repositories.users import UsersRepository


router = APIRouter()


@router.post("/", response_model=UserPublic, name="users:register-new-user", status_code=HTTP_201_CREATED)
async def register_new_user(
        new_user: UserCreate = Body(...),
        repo: UsersRepository = Depends(get_repository(UsersRepository)),
) -> UserPublic:
    created_user = await repo.register_new_user(new_user=new_user)
    access_token = AccessToken(
        access_token=auth_service.create_access_token_for_user(user=created_user), token_type="bearer"
    )
    return UserPublic(**created_user.dict(), access_token=access_token)
