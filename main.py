from fastapi import FastAPI

from routers.rating import rating_router
from routers.user import auth_router
from routers.course import course_router
from routers.lesson import lesson_router
from routers.comment import comment_router
from core.db import engine

from models import base

app = FastAPI()

base.Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(course_router)
app.include_router(lesson_router)
app.include_router(comment_router)
app.include_router(rating_router)