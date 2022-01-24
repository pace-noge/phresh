from typing import Optional, Union
from enum import Enum

from app.models.core import IDModelMixin, CoreModel
from app.models.user import UserPublic


class CleaningType(str, Enum):
    dust_up = "dust_up"
    spot_clean = "spot_clean"
    full_clean = "full_clean"


class CleaningBase(CoreModel):
    """
    All common characteristic of our cleaning resource.
    """
    name: Optional[str]
    description: Optional[str]
    price: Optional[float]
    cleaning_type: Optional[CleaningType] = "spot_clean"


class CleaningCreate(CleaningBase):
    name: str
    price: float


class CleaningUpdate(CleaningBase):
    cleaning_type: Optional[CleaningType]


class CleaningInDB(IDModelMixin, CleaningBase):
    name: str
    price: float
    cleaning_type: CleaningType
    owner: int


class CleaningPublic(IDModelMixin, CleaningBase):
    owner: Union[int, UserPublic]
