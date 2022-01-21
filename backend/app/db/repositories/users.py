from app.db.repositories.base import BaseRepository
from app.models.user import UserCreate, UserUpdate, UserInDB
from fastapi import HTTPException
from starlette import status
from databases import Database

from app.services import auth_service

GET_USER_BY_EMAIL_QUERY = """
    SELECT id, username, email, email_verified, password, salt, is_active, is_superuser, created_at, updated_at
    FROM users
    WHERE email = :email;
"""

GET_USER_BY_USERNAME_QUERY = """
    SELECT id, username, email, email_verified, password, salt, is_active, is_superuser, created_at, updated_at
    FROM users
    WHERE username = :username;
"""

REGISTER_NEW_USER_QUERY = """
    INSERT INTO users (username, email, password, salt)
    VALUES (:username, :email, :password, :salt)
    RETURNING id, username, email, email_verified, password, salt, is_active, is_superuser, created_at, updated_at;
"""


class UsersRepository(BaseRepository):
    def __init__(self, db: Database) -> None:
        super().__init__(db)
        self.auth_service = auth_service

    async def register_new_user(self, *, new_user: UserCreate) -> UserInDB:
        return None

    async def get_user_by_email(self, *, email: str) -> UserInDB:
        user = await self.db.fetch_one(query=GET_USER_BY_EMAIL_QUERY, values={"email": email})
        if not user:
            return None
        return UserInDB(**user)

    async def get_user_by_username(self, *, username: str) -> UserInDB:
        user = await self.db.fetch_one(query=GET_USER_BY_USERNAME_QUERY, values={"username": username})
        if not user:
            return None
        return UserInDB(**user)

    async def register_new_user(self, *, new_user: UserCreate) -> UserInDB:

        if await self.get_user_by_email(email=new_user.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email already taken. Login with that email or register with another one."
            )

        if await self.get_user_by_username(username=new_user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This username already taken. Please try another one."
            )

        user_password_update = self.auth_service.create_salt_and_hashed_password(plaintext_password=new_user.password)
        new_user_params = new_user.copy(update=user_password_update.dict())
        created_user = await self.db.fetch_one(query=REGISTER_NEW_USER_QUERY, values=new_user_params.dict())
        return UserInDB(**created_user)

