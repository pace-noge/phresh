from typing import List

import pytest
from databases import Database

from httpx import AsyncClient
from fastapi import FastAPI
from starlette import status

from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY, HTTP_201_CREATED, HTTP_200_OK, \
    HTTP_204_NO_CONTENT, HTTP_401_UNAUTHORIZED

from app.db.repositories.cleanings import CleaningsRepository
from app.models.cleaning import CleaningCreate, CleaningInDB, CleaningPublic
from app.models.user import UserInDB

pytestmark = pytest.mark.asyncio


@pytest.fixture
def new_cleaning():
    return CleaningCreate(
        name="Test Cleaning",
        description="description",
        price=0.00,
        cleaning_type="spot_clean"
    )


@pytest.fixture
async def test_cleaning_list(db: Database, test_user2: UserInDB) -> List[CleaningInDB]:
    cleaning_repo = CleaningsRepository(db)
    return [
        await cleaning_repo.create_cleaning(
            new_cleaning=CleaningCreate(
                name=f"test cleaning {i}", description="test description", price=20.00, cleaning_type="full_clean"
            ),
            requesting_user=test_user2
        )
        for i in range(5)
    ]

class TestCleaningRoutes:
    @pytest.mark.asyncio
    async def test_route_exists(self, app: FastAPI, client: AsyncClient) -> None:
        res = await client.post(app.url_path_for("cleanings:create-cleaning"), json={})
        assert res.status_code != HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_invalid_input_raises_error(self, app: FastAPI, authorized_client: AsyncClient) -> None:
        res = await authorized_client.post(app.url_path_for("cleanings:create-cleaning"), json={})
        assert res.status_code == HTTP_422_UNPROCESSABLE_ENTITY
        res = await authorized_client.get(app.url_path_for("cleanings:get-cleaning-by-id", cleaning_id="1"))
        assert res.status_code != HTTP_404_NOT_FOUND
        res = await authorized_client.get(app.url_path_for("cleanings:list-all-user-cleanings"))
        assert res.status_code != HTTP_404_NOT_FOUND
        res = await authorized_client.put(app.url_path_for("cleanings:update-cleaning-by-id", cleaning_id="1"))
        assert res.status_code != HTTP_404_NOT_FOUND
        res = await authorized_client.delete(app.url_path_for("cleanings:delete-cleaning-by-id", cleaning_id="0"))
        assert res.status_code != HTTP_404_NOT_FOUND


class TestCreateCleaning:
    async def test_valid_input_creates_cleaning_belonging_to_user(
            self,
            app: FastAPI,
            authorized_client: AsyncClient,
            test_user: UserInDB,
            new_cleaning: CleaningCreate
    ) -> None:
        res = await authorized_client.post(
            app.url_path_for("cleanings:create-cleaning"),
            json=new_cleaning.dict()
        )
        assert res.status_code == HTTP_201_CREATED
        created_cleaning = CleaningPublic(**res.json())
        assert created_cleaning.name == new_cleaning.name
        assert created_cleaning.price == new_cleaning.price
        assert created_cleaning.cleaning_type == new_cleaning.cleaning_type
        assert created_cleaning.owner == test_user.id

    async def test_unauthorized_user_unable_to_create_cleaning(
            self,
            app: FastAPI,
            client: AsyncClient,
            new_cleaning: CleaningCreate
    ) -> None:
        res = await client.post(app.url_path_for("cleanings:create-cleaning"), json=new_cleaning.dict())
        assert res.status_code == HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "invalid_payload, status_code",
        (
                (None, 422),
                ({}, 422),
                ({"name": "test name"}, 422),
                ({"price": 0.00}, 422),
                ({"name": "test_name", "description": "test"}, 422)
        )
    )
    async def test_invalid_input_raises_error(
            self,
            app: FastAPI,
            authorized_client: AsyncClient,
            invalid_payload: dict,
            status_code: int
    ) -> None:
        res = await authorized_client.post(app.url_path_for("cleanings:create-cleaning"), json=invalid_payload)
        assert status_code == res.status_code


class TestGetCleaning:
    async def test_get_cleaning_by_id(
            self,
            app: FastAPI,
            authorized_client: AsyncClient,
            test_cleaning: CleaningPublic
    ) -> None:
        print("Test Cleaning:", test_cleaning)
        res = await authorized_client.get(app.url_path_for("cleanings:get-cleaning-by-id", id=test_cleaning.id))
        assert res.status_code == HTTP_200_OK
        cleaning = CleaningInDB(**res.json())
        assert cleaning == test_cleaning

    async def test_unauthorized_users_cant_access_cleanings(
            self, app: FastAPI, client: AsyncClient, test_cleaning: CleaningInDB
    ) -> None:
        res = await client.get(app.url_path_for("cleanings:get-cleaning-by-id", cleaning_id=test_cleaning.id))
        assert res.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize(
        "id, status_code",
        (
                (500, 404),
                (-1, 404),
                (None, 422)
        ),
    )
    async def test_wrong_id_returns_error(self, app: FastAPI, authorized_client: AsyncClient, id: int, status_code: int) -> None:
        res = await authorized_client.get(app.url_path_for("cleanings:get-cleaning-by-id", id=id))
        assert res.status_code == status_code

    async def test_get_all_cleanings_returns_only_user_owned_cleanings(
            self, app: FastAPI, authorized_client: AsyncClient, test_user: UserInDB, db: Database,
            test_cleaning: CleaningInDB, test_cleaning_list: List[CleaningInDB]
    ) -> None:
        res = await authorized_client.get(app.url_path_for("cleanings:list-all-user-cleaings"))
        assert res.status_code == HTTP_200_OK
        assert isinstance(res.json(), list)
        assert len(res.json()) > 0
        cleanings = [CleaningInDB(**l) for l in res.json()]
        assert test_cleaning in cleanings
        for cleaning in cleanings:
            assert cleaning.owner == test_user.id
        assert all(c not in cleanings for c in test_cleaning_list)


class TestUpdateCleaning:
    @pytest.mark.parametrize(
        "attrs_to_change, values",
        (
                (["name"], ["new fake cleaning"]),
                (["description"], ["new fake cleaning description"]),
                (["price"], [3.14]),
                (["cleaning_type"], ["full_clean"]),
                (
                    ["name", "description"],
                    [
                        "extra new fake cleaning name",
                        "extra new fake cleaning description"
                    ],
                ),
                (["price", "cleaning_type"], [42.00, "dust_up"])
        )
    )
    async def test_update_cleaning_with_valid_input(
            self,
            app: FastAPI,
            authorized_client: AsyncClient,
            test_cleaning: CleaningInDB,
            attrs_to_change: List[str],
            values: List[str]
    ) -> None:
        cleaning_update = {attrs_to_change[i]: values[i] for i in range(len(attrs_to_change))}
        res = await authorized_client.put(app.url_path_for("cleanings:update-cleaning-by-id", id=test_cleaning.id), json=cleaning_update)
        assert res.status_code == HTTP_200_OK
        update_cleaning = CleaningInDB(**res.json())
        for i in range(len(attrs_to_change)):
            attr_to_change = getattr(update_cleaning, attrs_to_change[i])
            assert attr_to_change != getattr(test_cleaning, attrs_to_change[i])
            assert attr_to_change == values[i]

        for attr, value in update_cleaning.dict().items():
            if attr not in attrs_to_change:
                assert getattr(test_cleaning, attr) == value

    @pytest.mark.parametrize(
        "id, payload, status_code",
        (
                (-1, {"name": "test"}, 422),
                (0, {"name": "test2"}, 422),
                (500, {"name": "test3"}, 404),
                (1, None, 422),
                (1, {"cleaning_type": "invalid cleaning type"}, 422),
                (1, {"cleaning_type": None}, 400)
        )
    )
    async def test_update_cleaning_with_invalid_input_throws_error(
            self,
            app: FastAPI,
            client: AsyncClient,
            test_cleaning: CleaningInDB,
            id: int,
            payload: dict,
            status_code: int
    ) -> None:
        res = await client.put(app.url_path_for("cleanings:update-cleaning-by-id", id=id), json=payload)
        assert res.status_code == status_code


class TestDeleteCleaning:
    async def test_can_delete_cleaning_successfully(
            self,
            app: FastAPI,
            authorized_client: AsyncClient,
            test_cleaning: CleaningInDB,
    ) -> None:
        res = await authorized_client.delete(
            app.url_path_for(
                "cleanings:delete-cleaning-by-id",
                id=str(test_cleaning.id),
            ),
        )
        assert res.status_code == HTTP_204_NO_CONTENT
        res = await authorized_client.get(
            app.url_path_for(
                "cleanings:delete-cleaning-by-id",
                id=str(test_cleaning.id),
            )
        )
        assert res.status_code == HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "id, status_code",
        (
                (500, 404),
                (0, 422),
                (-1, 422),
                (None, 422)
        )
    )
    async def test_delete_cleaning_with_invalid_input_throws_error(
            self,
            app: FastAPI,
            client: AsyncClient,
            test_cleaning: CleaningInDB,
            id: int,
            status_code: int
    ) -> None:
        res = await client.delete(
            app.url_path_for("cleanings:delete-cleaning-by-id", id=id)
        )
        assert res.status_code == status_code
