from fastapi import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_403_FORBIDDEN

from app.db.repositories.base import BaseRepository
from app.models.cleaning import CleaningCreate, CleaningUpdate, CleaningInDB, CleaningPublic
from typing import List

from app.models.user import UserInDB

CREATE_CLEANING_QUERY = """
    INSERT INTO cleanings (name, description, price, cleaning_type, owner)
    VALUES (:name, :description, :price, :cleaning_type, :owner)
    RETURNING id, name, description, price, cleaning_type, owner, created_at, updated_at;
"""

GET_CLEANING_BY_ID_QUERY = """
    SELECT id, name, description, price, cleaning_type, owner
    FROM cleanings
    WHERE id = :id;
"""


GET_ALL_CLEANING_QUERY = """
    SELECT id, name, description, price, cleaning_type, owner
    FROM cleanings;
"""

UPDATE_CLEANING_BY_ID_QUERY = """
    UPDATE cleanings
    SET name            = :name,
        description     = :description,
        price           = :price,
        cleaning_type   = :cleaning_type,
        owner = :owner
    WHERE id = :id
    RETURNING id, name, description, price, cleaning_type, owner;
"""

DELETE_CLEANING_BY_ID_QUERY = """
    DELETE FROM cleanings
    WHERE id = :id
    RETURNING id;
"""

LIST_ALL_USER_CLEANINGS_QUERY = """
    SELECT id, name, description, price, cleaning_type, owner, created_at, updated_at
    FROM cleanings
    WHERE owner = :owner
"""


class CleaningsRepository(BaseRepository):
    async def create_cleaning(self, *, new_cleaning: CleaningCreate, requesting_user: UserInDB) -> CleaningPublic:
        cleaning = await self.db.fetch_one(
            query=CREATE_CLEANING_QUERY, values={**new_cleaning.dict(), "owner": requesting_user.id}
        )
        return CleaningPublic(**cleaning)

    async def get_cleaning_by_id(self, *, id: int, requesting_user: UserInDB) -> CleaningInDB:
        cleaning = await self.db.fetch_one(query=GET_CLEANING_BY_ID_QUERY, values={"id": id})
        if not cleaning:
            return None
        return CleaningInDB(**cleaning)

    async def list_all_user_cleanings(self, requesting_user: UserInDB) -> List[CleaningInDB]:
        cleanings = await self.db.fetch_all(query=LIST_ALL_USER_CLEANINGS_QUERY, values={"owner": requesting_user.id})
        return [CleaningInDB(**l) for l in cleanings]

    async def update_cleaning(
            self, *, cleaning: CleaningInDB, cleaning_update: CleaningUpdate
    ) -> CleaningPublic:
        cleaning_update_params = cleaning.copy(
            update=cleaning_update.dict(exclude_unset=True),
        )
        if cleaning_update_params.cleaning_type is None:
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid cleaning type. Cannot be None."
            )
        updated_cleaning = await self.db.fetch_one(
            query=UPDATE_CLEANING_BY_ID_QUERY,
            values=cleaning_update_params.dict()
        )
        return CleaningPublic(**updated_cleaning)

    async def delete_cleaning_by_id(self, *, cleaning: CleaningInDB) -> int:
        return await self.db.execute(query=DELETE_CLEANING_BY_ID_QUERY, values={"id": cleaning.id})
