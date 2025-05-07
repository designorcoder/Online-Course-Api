from models.base import BaseModel
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped


class Comment(BaseModel):
    __tablename__ = "comments"

    text: Mapped[str] = mapped_column(Text, nullable=True)
    lesson_id: Mapped[int] = mapped_column(ForeignKey("lesson.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))