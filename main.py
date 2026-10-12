from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated, TypeAlias

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import models
from database import Base, engine, get_db
from schemas import (
    PostCreate,
    PostResponse,
    PostUpdate,
    UserCreate,
    UserResponse,
    UserUpdate,
)


BASE_DIR = Path(__file__).resolve().parent
DbSession: TypeAlias = Annotated[Session, Depends(get_db)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="FastAPI Learn", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/media", StaticFiles(directory=BASE_DIR / "media"), name="media")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

sample_posts = [
    {
        "id": 1,
        "author": "Corey Schafer",
        "title": "FastAPI is Awesome",
        "content": "This framework is really easy to use and super fast.",
        "date_posted": "April 20, 2025",
    },
    {
        "id": 2,
        "author": "Jane Doe",
        "title": "Python is Great for Web Development",
        "content": "Python is a great language for web development, and FastAPI makes it even better.",
        "date_posted": "April 21, 2025",
    },
]


def find_user(db: Session, user_id: int) -> models.User:
    user = db.get(models.User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def find_post(db: Session, post_id: int) -> models.Post:
    post = db.get(models.Post, post_id)
    if post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return post


def ensure_user_identity_available(
    db: Session,
    name: str,
    email_address: str,
    exclude_user_id: int | None = None,
) -> None:
    query = select(models.User).where(
        or_(
            models.User.name == name,
            models.User.email_address == email_address,
        )
    )
    if exclude_user_id is not None:
        query = query.where(models.User.id != exclude_user_id)

    if db.scalar(query) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )


def commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The resource conflicts with existing data",
        ) from exc


@app.get("/")
@app.get("/home", include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"posts": sample_posts, "Title": "Home Page"},
    )


@app.get("/api/users", response_model=list[UserResponse])
def get_users(db: DbSession):
    return db.scalars(select(models.User).order_by(models.User.id)).all()


@app.get("/api/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: DbSession):
    return find_user(db, user_id)


@app.post(
    "/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
def create_user(user_data: UserCreate, db: DbSession):
    ensure_user_identity_available(
        db,
        name=user_data.name,
        email_address=str(user_data.email_address),
    )

    user = models.User(**user_data.model_dump())
    db.add(user)
    commit(db)
    db.refresh(user)
    return user


@app.put("/api/users/{user_id}", response_model=UserResponse)
def replace_user(user_id: int, user_data: UserCreate, db: DbSession):
    user = find_user(db, user_id)
    ensure_user_identity_available(
        db,
        name=user_data.name,
        email_address=str(user_data.email_address),
        exclude_user_id=user_id,
    )

    for field, value in user_data.model_dump().items():
        setattr(user, field, value)
    commit(db)
    db.refresh(user)
    return user


@app.patch("/api/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: DbSession):
    user = find_user(db, user_id)
    update_data = user_data.model_dump(exclude_unset=True)
    ensure_user_identity_available(
        db,
        name=update_data.get("name", user.name),
        email_address=str(update_data.get("email_address", user.email_address)),
        exclude_user_id=user_id,
    )

    for field, value in update_data.items():
        setattr(user, field, value)
    commit(db)
    db.refresh(user)
    return user


@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: DbSession) -> Response:
    user = find_user(db, user_id)
    db.delete(user)
    commit(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/api/users/{user_id}/posts", response_model=list[PostResponse])
def get_user_posts(user_id: int, db: DbSession):
    find_user(db, user_id)
    return db.scalars(
        select(models.Post)
        .where(models.Post.user_id == user_id)
        .order_by(models.Post.id)
    ).all()


@app.get("/api/posts", response_model=list[PostResponse])
def get_posts(db: DbSession):
    return db.scalars(select(models.Post).order_by(models.Post.id)).all()


@app.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: DbSession):
    return find_post(db, post_id)


@app.post(
    "/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED
)
def create_post(post_data: PostCreate, db: DbSession):
    find_user(db, post_data.user_id)
    post = models.Post(**post_data.model_dump())
    db.add(post)
    commit(db)
    db.refresh(post)
    return post


@app.put("/api/posts/{post_id}", response_model=PostResponse)
def replace_post(post_id: int, post_data: PostCreate, db: DbSession):
    post = find_post(db, post_id)
    find_user(db, post_data.user_id)

    for field, value in post_data.model_dump().items():
        setattr(post, field, value)
    commit(db)
    db.refresh(post)
    return post


@app.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: PostUpdate, db: DbSession):
    post = find_post(db, post_id)
    update_data = post_data.model_dump(exclude_unset=True)
    if "user_id" in update_data:
        find_user(db, update_data["user_id"])

    for field, value in update_data.items():
        setattr(post, field, value)
    commit(db)
    db.refresh(post)
    return post


@app.delete("/api/posts/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(post_id: int, db: DbSession) -> Response:
    post = find_post(db, post_id)
    db.delete(post)
    commit(db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

