import jwt
import pytest
from databases import Database

from httpx import AsyncClient
from fastapi import FastAPI
from pydantic import ValidationError
from starlette.datastructures import Secret
from typing import Union, Type

from starlette.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY
)

from app.core.config import SECRET_KEY, JWT_AUDIENCE, ACCESS_TOKEN_EXPIRE_MINUTES, JWT_ALGORITHM
from app.models.user import UserCreate, UserInDB, UserPublic
from app.db.repositories.users import UsersRepository
from app.services import auth_service


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
            "username": "bilal2408",
            "password": "password123"
        }
        user_in_db = await user_repo.get_user_by_email(email=new_user["email"])
        assert user_in_db is None

        res = await client.post(app.url_path_for("users:register-new-user"), json=new_user)
        assert res.status_code == HTTP_201_CREATED

        user_in_db = await user_repo.get_user_by_email(email=new_user["email"])
        assert user_in_db is not None
        assert user_in_db.email == new_user["email"]
        assert user_in_db.username == new_user["username"]

        created_user = UserPublic(**res.json()).dict(exclude={"access_token"})
        assert created_user == user_in_db.dict(exclude={"password", "salt"})

    @pytest.mark.parametrize(
        "attr, value, status_code",
        (
                ("email", "bilalbilal@mail.io", 400),
                ("username", "bilal2408", 400),
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

    async def test_user_saved_password_is_hashed_and_has_salt(
            self,
            app: FastAPI,
            client: AsyncClient,
            db: Database
    ) -> None:
        user_repo = UsersRepository(db)
        new_user = {"email": "beyonce@knowles.io", "username": "queenbey", "password": "destinyschild"}

        res = await client.post(app.url_path_for("users:register-new-user"), json=new_user)
        assert res.status_code == HTTP_201_CREATED

        user_in_db = await user_repo.get_user_by_email(email=new_user["email"])
        assert user_in_db is not None
        assert user_in_db.salt is not None and user_in_db.salt != "123"
        assert user_in_db.password != new_user["password"]
        assert auth_service.verify_password(
            password=new_user["password"],
            salt=user_in_db.salt,
            hashed_pw=user_in_db.password
        )


class TestAuthTokens:
    async def test_can_create_access_token_successfully(
            self,
            app: FastAPI,
            client: AsyncClient,
            test_user: UserInDB
    ) -> None:
        access_token = auth_service.create_access_token_for_user(
            user=test_user,
            secret_key=str(SECRET_KEY),
            audience=JWT_AUDIENCE,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        creds = jwt.decode(access_token, str(SECRET_KEY), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM])
        assert creds.get("username") is not None
        assert creds["username"] == test_user.username
        assert creds["aud"] == JWT_AUDIENCE

    async def test_token_missing_user_is_invalid(self, app: FastAPI, client: AsyncClient) -> None:
        access_token =auth_service.create_access_token_for_user(
            user=None,
            secret_key=str(SECRET_KEY),
            audience=JWT_AUDIENCE,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES
        )
        with pytest.raises(jwt.PyJWTError):
            jwt.decode(access_token, str(SECRET_KEY), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM])

    @pytest.mark.parametrize(
        "secret_key, jwt_audience, exception",
        (
                ("wrong-secret", JWT_AUDIENCE, jwt.InvalidSignatureError),
                (None, JWT_AUDIENCE, jwt.InvalidSignatureError),
                (SECRET_KEY, "othersite:auth", jwt.InvalidAudienceError),
                (SECRET_KEY, None, ValidationError)
        )
    )
    async  def test_invalid_token_content_raises_error(
            self,
            app: FastAPI,
            client: AsyncClient,
            test_user: UserInDB,
            secret_key: Union[str, Secret],
            jwt_audience: str,
            exception: Type[BaseException]
    ) -> None:
        with pytest.raises(exception):
            access_token = auth_service.create_access_token_for_user(
                user=test_user,
                secret_key=str(secret_key),
                audience=jwt_audience,
                expires_in=ACCESS_TOKEN_EXPIRE_MINUTES
            )
            jwt.decode(access_token, str(SECRET_KEY), audience=JWT_AUDIENCE, algorithms=[JWT_ALGORITHM])