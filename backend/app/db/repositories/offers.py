from typing import List

from fastapi import HTTPException, status
from asyncpg.exceptions import UniqueViolationError

from app.db.repositories.base import BaseRepository
from app.models.offer import OfferCreate, OfferUpdate, OfferInDB


CREATE_OFFER_FOR_CLEANING_QUERY = """
    INSERT INTO user_offers_for_cleanings (cleaning_id, user_id, status)
    VALUES (:cleaning_id, :user_id, :status)
    RETURNING cleaning_id, user_id, status, created_at, updated_at;
"""


class OffersRepository(BaseRepository):
    async def create_offer_for_cleaning(self, *, new_offer: OfferCreate) -> OfferInDB:
        try:
            created_offer = await self.db.fetch_one(
                query=CREATE_OFFER_FOR_CLEANING_QUERY, values={**new_offer.dict(), "status": "pending"}
            )
            return OfferInDB(**created_offer)
        except UniqueViolationError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Users aren't allowed create more than one offer for cleaning job."
            )
