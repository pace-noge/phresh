import pytest
from databases import Database

from httpx import AsyncClient
from fastapi import FastAPI

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY
)
from app.models.user import UserCreate, UserInDB
from app.db.repositories.users import UsersRepository


pytesmark = pytest.mark.asyncio


class TestUserRoutes:
    async def test_route_exists(self, app: FastAPI, client: AsyncClient) -> None:
        new_user = {"email": "test@mail.io", "username": "test_username", "password": "testpassword"}
        res = await client.post(app.url_path_for("users:register-new-user"), json=new_user)
        assert res.status_code != HTTP_404_NOT_FOUND


class TestUserRegistration:
    async def test_users_can_register_successfully(
            self,
            app: FastAPI,
            client: AsyncClient,
            db: Database
    ) -> None:
        user_repo = UsersRepository(db)
        new_user = {
            "email": "bilalbilal@mail.io",
            "username": "bilal24",
            "password": "password123"
        }
        user_in_db = await user_repo.get_user_by_email(email=new_user["email"])
        assert user_in_db is None

        res = await client.post(app.url_path_for("users:register-new-user"), json=new_user)
        assert res.status_code == HTTP_201_CREATED

        user_in_db =   await user_repo.get_user_by_email(email=new_user["email"])
        assert user_in_db is not None
        assert user_in_db.email == new_user["email"]
        assert user_in_db.username == new_user["username"]

        created_user = UserInDB(**res.json(), password="whatever", salt=123).dict(exclude={"password", "salt"})
        assert created_user == user_in_db.dict(exclude={"password", "salt"})


    @pytest.mark.parametrize(
        "attr, value, status_code",
        (
                ("email", "bilalbilal@mail.io", 400),
                ("username", "bilal24", 400),
                ("email", "invalid.email@one@two.io", 422),
                ("password", "short", 422),
                ("username", "shakira@#$%^<>", 422),
                ("username", "ab", 422)
        )
    )
    async def test_user_registration_fail_when_credentials_are_taken(
            self,
            app: FastAPI,
            client: AsyncClient,
            db: Database,
            attr: str,
            value: str,
            status_code: int
    ) -> None:
        new_user = {"email": "nottaken@email.io", "username": "not_taken_username", "password": "freepassword",
                    attr: value}

        res = await client.post(app.url_path_for("users:register-new-user"), json=new_user)
        assert res.status_code == status_code
