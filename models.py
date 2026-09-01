from datetime import datetime, UTC
from sqlalchemy import DateTime, Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id : Mapped[int] = mapped_column(Integer, index=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False )
    email_address: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    image_file : Mapped[str |None] = mapped_column(String(200))
    posts: Mapped[list[Posts]] = relationship(back_populates="author")


    @property
    def image_path(self) -> str:
        if self.image_file:
            return f"/media/profile_pics/{self.image_file}"
        return "/static/profile_pics/default.jpg"


class Posts(Base):
    __tablename__ = "posts"
    id : Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[int]= mapped_column(String(100),nullable=False )
    content: Mapped[str]= mapped_column(Text, nullable=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True,
        nullable=False
    )
    date_posted : Mapped[datetime]= mapped_column(
        DateTime(timezone=True),
        default = lambda: datetime.now(UTC)
    )
    author: Mapped[User] = relationship(back_populates="posts")