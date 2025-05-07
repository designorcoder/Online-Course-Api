from pydantic import BaseModel, Field


class RatingOut(BaseModel):
    id: int
    author_id: int
    lesson_id: int
    starts: int = Field(ge=1, le=5)  # 1 to 5


class RatingCreate(BaseModel):
    lesson_id: int
    starts: int = Field(ge=1, le=5)  # 1 to 5


class RatingUpdate(BaseModel):
    lesson_id: int
    starts: int = Field(ge=1, le=5)  # 1 to 5