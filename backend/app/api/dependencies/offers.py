from fastapi import HTTPException, Depends, status

from app.models.user import UserInDB
from app.models.cleaning import CleaningInDB
from app.db.repositories.offers import OffersRepository