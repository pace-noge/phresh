from typing import List
from fastapi import APIRouter, Path, Body, status, Depends, HTTPException

from app.models.offer import OfferCreate, OfferUpdate, OfferInDB, OfferPublic
from app.models.cleaning import CleaningInDB
from app.models.user import UserInDB

from app.api.dependencies.cleanings import get_cleaning_by_id_from_path, get_current_active_user
# from app.api.dependencies.offers import check_offer_create_permissions
from app.db.repositories.offers import OffersRepository
from app.api.dependencies.database import get_repository


router = APIRouter()


@router.post(
    "/",
    response_model=OfferPublic,
    name="offers:create-offer",
    status_code=status.HTTP_201_CREATED
)
async def create_offer(
        cleaning: CleaningInDB = Depends(get_cleaning_by_id_from_path),
        current_user: UserInDB = Depends(get_current_active_user),
        offers_repo: OffersRepository = Depends(get_repository(OffersRepository)),
) -> OfferPublic:
    if cleaning.owner == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Users are unable to create offers for cleaning jobs they own."
        )
    new_offer = OfferCreate(cleaning_id=cleaning.id, user_id=current_user.id)
    return await offers_repo.create_offer_for_cleaning(new_offer=new_offer)


@router.get("/", response_model=List[OfferPublic], name="offers:list-offers-for-cleaning")
async def list_offer_for_cleanings(offer_create: OfferCreate = Body(...)) -> OfferPublic:
    return None


@router.get("/{username}/", response_model=OfferPublic, name="offers:get-offer-from-user")
async def get_offer_from_user(username: str = Path(..., min_length=3)) -> OfferPublic:
    return None


@router.put("/{username}/", response_model=OfferPublic, name="offers:accept-offer-from-user")
async def accept_offer_from_user(username: str = Path(..., min_length=3)) -> OfferPublic:
    return None


@router.put("/", response_model=OfferPublic, name="offers:cancel-offer-from-user")
async def cancel_offer_from_user() -> OfferPublic:
    return None


@router.delete("/", response_model=int, name="offers:rescind-offer-from-user")
async def rescind_offer_from_user() -> OfferPublic:
    return None
