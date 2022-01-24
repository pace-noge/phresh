from typing import Optional
from pydantic import EmailStr, HttpUrl
from app.models.core import DateTimeModelMixin, IDModelMixin, CoreModel


class ProfileBase(CoreModel):
    full_name: Optional[str]
    phone_number: Optional[str]
    bio: Optional[str]
    image: Optional[HttpUrl]


class ProfileCreate(ProfileBase):
    """
    The only field required for user profile is user_id
    """
    user_id: int


class ProfileUpdate(ProfileBase):
    """
    Allow user to update any field.
    """
    pass


class ProfileInDB(IDModelMixin, DateTimeModelMixin, ProfileBase):
    user_id: int
    username: Optional[str]
    email: Optional[EmailStr]


class ProfilePublic(ProfileInDB):
    pass

