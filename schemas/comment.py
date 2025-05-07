from pydantic import BaseModel
from datetime import datetime


class CommentOut(BaseModel):
    id: int
    lesson_id: int
    author_id: int
    text: str
    created_at: datetime


class CommentCreate(BaseModel):
    lesson_id: int
    text: str


class CommentUpdate(BaseModel):
    text: str