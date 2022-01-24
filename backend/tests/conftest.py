import os
import warnings

import alembic
import pytest
import pytest_asyncio
from alembic.config import Config
from asgi_lifespan import LifespanManager
from databases import Database
from fastapi import FastAPI
from httpx import AsyncClient

from app.core.config import SECRET_KEY, JWT_TOKEN_PREFIX
from app.db.repositories.cleanings import CleaningsRepository
from app.db.repositories.users import UsersRepository
from app.models.cleaning import CleaningInDB, CleaningCreate, CleaningPublic
from app.models.user import UserInDB, UserCreate, UserPublic
from app.services import auth_service


@pytest_asyncio.fixture(scope="session")
def apply_migrations():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    os.environ["TESTING"] = "1"
    config = Config("alembic.ini")

    alembic.command.upgrade(config, "head")
    yield
    alembic.command.downgrade(config, "base")


@pytest.fixture
def app(apply_migrations: None) -> FastAPI:
    from app.api.server import get_application
    return get_application()


@pytest.fixture
def db(app: FastAPI) -> Database:
    return app.state._db


@pytest.fixture
async def client(app: FastAPI) -> AsyncClient:
    async with LifespanManager(app):
        async with AsyncClient(
            app=app,
            base_url="http://testserver",
            headers={"Content-Type": "application/json"}
        ) as client:
            yield client


@pytest.fixture
async def test_user(db: Database) -> UserPublic:
    new_user = UserCreate(
        email="lebron@james.io",
        username="lebronjames",
        password="password123"
    )

    user_repo = UsersRepository(db)

    existing_user = await user_repo.get_user_by_email(email=new_user.email, populate=True)
    if existing_user:
        return existing_user
    newly_created = await user_repo.register_new_user(new_user=new_user)
    return newly_created


@pytest.fixture
async def test_cleaning(db: Database, test_user: UserPublic) -> CleaningPublic:
    cleaning_repo = CleaningsRepository(db)
    new_cleaning = CleaningCreate(
        name="fake cleaning name",
        description="fake cleaning description",
        price=9.99,
        cleaning_type="spot_clean"
    )
    return await cleaning_repo.create_cleaning(new_cleaning=new_cleaning, requesting_user=test_user)


@pytest.fixture
async def authorized_client(client: AsyncClient, test_user: UserInDB) -> AsyncClient:
    access_token = auth_service.create_access_token_for_user(user=test_user, secret_key=str(SECRET_KEY))
    client.headers = {
        **client.headers,
        "Authorization": f"{JWT_TOKEN_PREFIX} {access_token}"
    }
    return client


@pytest.fixture
async def test_user2(db: Database) -> UserInDB:
    new_user = UserCreate(
        email="serena@williams.io",
        username="serenawilliams",
        password="tennistwins",
    )
    user_repo = UsersRepository(db)
    existings_user = await user_repo.get_user_by_email(email=new_user.email, populate=True)
    if existings_user:
        return existings_user
    return await user_repo.register_new_user(new_user=new_user)