import string
from typing import Optional
from pydantic import EmailStr, constr, validator


from app.models.core import DateTimeModelMixin, IDModelMixin, CoreModel
from app.models.profile import ProfilePublic
from app.models.token import AccessToken


def validate_username(username: str) -> str:
    allowed = string.ascii_letters + string.digits + "-" + "_"
    assert all(char in allowed for char in username), "Invalid characters in username."
    assert len(username) >= 3, "Username must be 3 characters or more"
    return username


class UserBase(CoreModel):
    """
    Leaving off password and salt from base model
    """
    email: Optional[EmailStr]
    username: Optional[str]
    email_verified: bool = False
    is_active: bool = True
    is_superuser: bool = False


class UserCreate(CoreModel):
    """
    Email, Username, Password are required for registering user.
    """
    email: EmailStr
    password: constr(min_length=7, max_length=100)
    username: str

    @validator("username", pre=True)
    def username_is_valid(cls, username: str) -> str:
        return validate_username(username)


class UserPasswordUpdate(CoreModel):
    """
    Users can change their password
    """
    password: constr(min_length=7, max_length=100)
    salt: str


class UserInDB(IDModelMixin, DateTimeModelMixin, UserBase):
    """
    Add in id, created_at, updated_at, and user's password and salt
    """
    password: constr(min_length=7, max_length=100)
    salt: str


class UserPublic(IDModelMixin, DateTimeModelMixin, UserBase):
    access_token: Optional[AccessToken]
    profile: Optional[ProfilePublic]


class UserUpdate(CoreModel):
    """
    User are allowed to update their email and username
    """
    email: Optional[str]
    username: Optional[constr(min_length=3, regex="^[a-zA-Z0-9-_]+$")]
