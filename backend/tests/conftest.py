import os
import warnings
from typing import List, Callable

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
from app.db.repositories.offers import OffersRepository
from app.db.repositories.users import UsersRepository
from app.models.cleaning import CleaningInDB, CleaningCreate, CleaningPublic
from app.models.offer import OfferCreate, OfferUpdate
from app.models.user import UserInDB, UserCreate, UserPublic
from app.services import auth_service


async def user_fixture_helper(*, db: Database, new_user: UserCreate) -> UserPublic:
    user_repo = UsersRepository(db)
    existing_user = await user_repo.get_user_by_email(email=new_user.email)
    if existing_user:
        return existing_user
    return await user_repo.register_new_user(new_user=new_user)


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
    return await user_fixture_helper(db=db, new_user=new_user)


@pytest.fixture
async def test_user2(db: Database) -> UserPublic:
    new_user = UserCreate(email="serena@williams.io", username="serenawilliams", password="tennistwins")
    return await user_fixture_helper(db=db, new_user=new_user)


@pytest.fixture
async def test_user3(db: Database) -> UserPublic:
    new_user = UserCreate(email="brad@pitt.io", username="bradpitt", password="adastra")
    return await user_fixture_helper(db=db, new_user=new_user)


@pytest.fixture
async def test_user4(db: Database) -> UserInDB:
    new_user = UserCreate(email="jennifer@lopez.io", username="jlo", password="jennyfromtheblock")
    return await user_fixture_helper(db=db, new_user=new_user)


@pytest.fixture
async def test_user5(db: Database) -> UserInDB:
    new_user = UserCreate(email="bruce@lee.io", username="brucelee", password="martialarts")
    return await user_fixture_helper(db=db, new_user=new_user)


@pytest.fixture
async def test_user6(db: Database) -> UserInDB:
    new_user = UserCreate(email="kal@penn.io", username="kalpenn", password="haroldandkumar")
    return await user_fixture_helper(db=db, new_user=new_user)


@pytest.fixture
async def test_user_list(
    test_user3: UserInDB, test_user4: UserInDB, test_user5: UserInDB, test_user6: UserInDB,
) -> List[UserInDB]:
    return [test_user3, test_user4, test_user5, test_user6]


@pytest.fixture
def create_authorized_client(client: AsyncClient) -> Callable:
    def _create_authorized_client(*, user: UserInDB) -> AsyncClient:
        access_token = auth_service.create_access_token_for_user(user=user, secret_key=str(SECRET_KEY))
        client.headers = {
            **client.headers,
            "Authorization": f"{JWT_TOKEN_PREFIX} {access_token}"
        }
        return client
    return _create_authorized_client


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
async def test_cleaning_with_offers(db: Database, test_user2: UserInDB, test_user_list: [UserInDB]) -> CleaningInDB:
    cleaning_repo = CleaningsRepository(db)
    offers_repo = OffersRepository(db)
    new_cleaning = CleaningCreate(
        name="cleaning with offers", description="desc for cleaning", price=9.99, cleaning_repo="full_clean"
    )
    created_cleaning = await cleaning_repo.create_cleaning(new_cleaning=new_cleaning, requesting_user=test_user2)

    for user in test_user_list:
        await offers_repo.create_offer_for_cleaning(
            new_offer=OfferCreate(cleaning_id=created_cleaning.id, user_id=user.id)
        )
    return created_cleaning

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


@pytest.fixture
async def test_cleaning_with_offers(db: Database, test_user2: UserInDB, test_user_list: List[UserInDB]) -> CleaningInDB:
    cleaning_repo = CleaningsRepository(db)
    offers_repo = OffersRepository(db)

    new_cleaning = CleaningCreate(
        name="cleaning with offers", description="desc for cleaning", price=9.99, cleaning_type="full_clean"
    )
    created_cleaning = await cleaning_repo.create_cleaning(new_cleaning=new_cleaning, requesting_user=test_user2)
    for user in test_user_list:
        await offers_repo.create_offer_for_cleaning(
            new_offer=OfferCreate(cleaning_id=created_cleaning.id, user_id=user.id)
        )
    return created_cleaning


@pytest.fixture
async def test_cleaning_with_accepted_offer(
        db: Database, test_user2: UserInDB, test_user3: UserInDB, test_user_list: List[UserInDB]
) -> CleaningInDB:
    cleaning_repo = CleaningsRepository(db)
    offers_repo = OffersRepository(db)
    new_cleaning = CleaningCreate(
        name="Cleaning with offers", description="desc for cleaning", price=9.99, cleaning_type="full_clean"
    )
    created_cleaning = await cleaning_repo.create_cleaning(new_cleaning=new_cleaning, requesting_user=test_user2)
    offers = []
    for user in test_user_list:
        offers.append(
            await offers_repo.create_offer_for_cleaning(
                new_offer=OfferCreate(cleaning_id=created_cleaning.id, user_id=user.id)
            )
        )
    await offers_repo.accept_offer(
        offer=[o for o in offers if o.user_id == test_user3.id][0], offer_update=OfferUpdate(status="accepted")
    )
    return created_cleaning
