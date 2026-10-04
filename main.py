from sys import exception

from fastapi import FastAPI, Request, HTTPException, status, Depends
# from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
import models
from database import Base, engine, get_db
from schemas import PostCreate, PostResponse, UserCreate, UserResponse, PostUpdate
from typing import Annotated

Base.metadata.create_all(bind=engine)
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"),name="static")

app.mount("/media", StaticFiles(directory="media"),name="media")

templates = Jinja2Templates(directory="templates")
posts: list[dict] = [
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
@app.get("/")
@app.get("/home", include_in_schema=False)
def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"posts": posts, "Title":"Home Page"},
    )

@app.get("/api/user/{user_id}", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def get_user(user_id: int, db: Annotated[Session, Depends(get_db)]):
    User = db.execute(
        select(models.User).where(models.User.id== user_id)
    ).scalars().first()
    if User:
        return User
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="User not found")



@app.get("/api/post/{post_id}", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def get_post_by_id(post_id: int, db: Annotated[Session, Depends(get_db)]):
    post = db.execute(
        select(models.Posts).where(models.Posts.id== post_id)
    ).scalars().first()
    if post:
        return post
    raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")


@app.put("/api/post/{post_id}", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def update_post_full(post_id: int, post_data:PostCreate ,db: Annotated[Session, Depends(get_db)]):
    post = db.execute(
        select(models.Posts).where(models.Posts.id== post_id)
    ).scalars().first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")
    if post_data.user_id != post.user_id:
        user = db.execute(
                select(models.User).where(models.User.id == post.user_id)
            ).scalars().first()
        if not user:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="user not found")

    post.title = post_data.title
    post.content = post_data.content
    post.user_id = post_data.user_id

    db.commit()
    db.refresh(post)
    return post


@app.patch("/api/post/{post_id}", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def update_post_partial(post_id: int, post_data:PostUpdate ,db: Annotated[Session, Depends(get_db)]):
    post = db.execute(
        select(models.Posts).where(models.Posts.id== post_id)
    ).scalars().first()
    if not post:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="Post not found")

    update_data = post_data.model_dump(
        exclude_unset= True
    )
    for field, value in update_data.items():
        setattr(post, field, value)
        
    db.commit()
    db.refresh(post)
    return post

@app.get("/api/users", response_model=list[UserResponse])
def get_user(db: Annotated[Session, Depends(get_db)]):
     return db.execute(select(models.User)).scalars().all()


@app.get("/api/posts", response_model=list[PostResponse])
def get_all_posts(db: Annotated[Session, Depends(get_db)]):
    return db.execute(select(models.Posts)).scalars().all()

@app.get("/api/user/{user_id}/posts", response_model=list[PostResponse], status_code=status.HTTP_201_CREATED)
def get_post(user_id:int, db: Annotated[Session, Depends(get_db)]):
    user = db.execute(
        select(models.User).where(models.User.id == user_id)
    ).scalars().first()
    if not user:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail="User not found")
    result = db.execute(
        select(models.Posts).where(models.Posts.user_id== user_id)
    )
    posts = result.scalars().all()
    return posts

@app.post("/api/user",response_model= UserResponse, status_code= status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Annotated[Session, Depends(get_db)]):
    result = db.execute(
        select(models.User).where(models.User.name == user.name ),
    )
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code= status.HTTP_400_BAD_REQUEST,
            detail = "Username already exists"
        )

    result = db.execute(
        select(models.User).where(models.User.email_address== user.email_address),
    )
    existing_email = result.scalars().first()
    if existing_email:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail =" email already exists"
        )
    new_user = models.User(
        name = user.name,
        email_address = user.email_address
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/posts",response_model=PostResponse,status_code= status.HTTP_201_CREATED)
def create_post(post: PostCreate, db:Annotated[Session, Depends(get_db)]):
    result= db.execute(
        select(models.User).where(models.User.id==post.user_id)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail='User not found'
        )
    new_post = models.Posts(
        title= post.title,
        content= post.content,
        user_id= post.user_id

    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

# @app.get("/posts", include_in_schema=False)
# def get_posts():
#     html_content = "<html><body>"
#     for post in posts:
#         html_content += f"<h2>{post['title']}</h2>"
#         html_content += f"<p><strong>Author:</strong> {post['author']}</p>"
#         html_content += f"<p>{post['content']}</p>"
#         html_content += f"<p><em>{post['date_posted']}</em></p>"
#         html_content += "<hr>"
#     html_content += "</body></html>"
#     return HTMLResponse(content=html_content)


@app.get("/api/posts")
def get_posts():
    return posts

@app.get("/api/posts/{post_id}")
def get_post_by_id(post_id:int):
    for post in posts:
        if post["id"]== post_id:
            return post
    raise HTTPException(status_code=404, detail="Post not found")

@app.exception_handler(StarletteHTTPException)
def exception_handler(request: Request, exc: StarletteHTTPException):
    message = (exc.detail if exc.detail else "An error occurred")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": message},
    )

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    if request.url.path.startswith("/api"):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"message": "Validation error", "details": exc.errors()},
        )
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": "Validation error", "details": exc.errors()},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )

