from fastapi import APIRouter, status, HTTPException
from models.course import Course
from core.dependencies import DBSessionDep, CurrentUserDep
from schemas.course import CourseCreate, CourseOut, CourseUpdate

course_router = APIRouter(
    prefix="/course",
    tags=["course"]
)


@course_router.get("/", response_model=list[CourseOut])
async def get_all_courses(db: DBSessionDep, user: CurrentUserDep):
    data = db.query(Course).filter(user.get("id") == Course.author_id)
    return data


@course_router.post("/", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
async def create_course(db: DBSessionDep, course: CourseCreate, user: CurrentUserDep):
    new_course = Course(
        title=course.title,
        description=course.description,
        author_id=user.get("id")
    )
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@course_router.put("/{course_id}", response_model=CourseOut, status_code=status.HTTP_200_OK)
async def update_course(course_id: int, course: CourseUpdate, db: DBSessionDep, user: CurrentUserDep):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )

    if db_course.author_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz faqat o'zingizning kurslaringizni yangilay olasiz"  # noqa
        )

    for field, value in course.dict(exclude_unset=True).items():
        setattr(db_course, field, value)

    db.commit()
    db.refresh(db_course)
    return db_course


@course_router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(course_id: int, db: DBSessionDep, user: CurrentUserDep):
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    if db_course.author_id != user.get("id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz faqat o'zingizning kurslaringizni o'chira olasiz"  # noqa
        )
    db.delete(db_course)
    db.commit()
    return None