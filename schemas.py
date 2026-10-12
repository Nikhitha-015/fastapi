from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    email_address: EmailStr = Field(max_length=254)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=50)
    email_address: EmailStr | None = Field(default=None, max_length=254)

    @field_validator("name", "email_address")
    @classmethod
    def reject_null(cls, value: str | EmailStr | None) -> str | EmailStr:
        if value is None:
            raise ValueError("must not be null")
        return value


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_path: str | None
    image_file: str | None = None


class PostBase(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    content: str = Field(min_length=1)


class PostCreate(PostBase):
    user_id: int = Field(gt=0)


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    content: str | None = Field(default=None, min_length=1)
    user_id: int | None = Field(default=None, gt=0)

    @field_validator("title", "content", "user_id")
    @classmethod
    def reject_null(cls, value: str | int | None) -> str | int:
        if value is None:
            raise ValueError("must not be null")
        return value


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    date_posted: datetime
    author: UserResponse
