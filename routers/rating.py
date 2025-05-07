from fastapi import APIRouter, status, HTTPException
from models.rating import Rating
from models.course import Lesson
from core.dependencies import DBSessionDep, CurrentUserDep
from schemas.raiting import RatingCreate, RatingOut, RatingUpdate

rating_router = APIRouter(
    prefix="/rating",
    tags=["rating"]
)


@rating_router.get("/", response_model=list[RatingOut], status_code=status.HTTP_200_OK)
async def get_rating(db: DBSessionDep):
    db_rating = db.query(Rating).all()
    return db_rating


@rating_router.post("/", response_model=RatingOut, status_code=status.HTTP_201_CREATED)
async def create_rating(db: DBSessionDep, rating: RatingCreate, user: CurrentUserDep):
    db_rating = db.query(Lesson).filter(Lesson.id == rating.lesson_id).first()
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sizda bunday id {rating.lesson_id} dars mavjud emas!"  # noqa
        )
    new_rating = Rating(
        author_id=user.get("id"),
        lesson_id=rating.lesson_id,
        starts=rating.starts

    )
    db.add(new_rating)
    db.commit()
    return db_rating


@rating_router.put("/{rating_id}", response_model=RatingOut, status_code=status.HTTP_200_OK)
async def lesson_update(rating_id: int, db: DBSessionDep, user: CurrentUserDep, rating: RatingUpdate):
    db_rating = db.query(Rating).filter(Rating.id == rating_id).first()
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sizda bunday id {rating_id} dars mavjud emas!"  # noqa
        )

    for field, value in rating.dict(exclude_unset=True).items():
        setattr(db_rating, field, value)

    db.commit()
    db.refresh(db_rating)
    return db_rating


@rating_router.delete("/{rating_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(rating_id: int, db: DBSessionDep, user: CurrentUserDep):
    db_rating = db.query(Rating).filter(Lesson.id == rating_id).first()
    if not db_rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sizda bunday id {rating_id} dars mavjud emas!"  # noqa
        )

    db.delete(db_rating)
    db.commit()
    return None