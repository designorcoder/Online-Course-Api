from fastapi import APIRouter, HTTPException, status
from models.course import Course, Lesson
from core.dependencies import DBSessionDep, CurrentUserDep
from schemas.lesson import LessonCreate, LessonOut, LessonUpdate

lesson_router = APIRouter(
    prefix="/lesson",
    tags=["lesson"]
)


@lesson_router.get("/", response_model=list[LessonOut])
async def get_all_lessons(db: DBSessionDep):
    data = db.query(Lesson).all()
    return data


@lesson_router.post("/", response_model=LessonOut, status_code=status.HTTP_201_CREATED)
async def create_lesson(lesson: LessonCreate, db: DBSessionDep, user: CurrentUserDep):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    course = db.query(Course).filter(Course.id == lesson.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Bu ID dagi kurs {lesson.course_id} topilmadi"
        )
    if course.author_id != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz faqat ozingizni kurslaringizga dars qo'shishingiz mumkin"
        )
    lesson_data = lesson.dict()
    new_lesson = Lesson(**lesson_data)

    db.add(new_lesson)
    db.commit()
    db.refresh(new_lesson)
    return new_lesson


@lesson_router.put("/{lesson_id}", response_model=LessonOut, status_code=status.HTTP_200_OK)
async def update_lesson(lesson_id: int, lesson: LessonUpdate, db: DBSessionDep, user: CurrentUserDep):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found"
        )
    course = db.query(Course).filter(Course.id == db_lesson.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {db_lesson.course_id} not found"
        )
    if course.author_id != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz faqat ozingizni kurslaringizdagi darslarni o'zgartirishingiz mumkin"
        )
    for field, value in lesson.dict(exclude_unset=True).items():
        setattr(db_lesson, field, value)

    db.commit()
    db.refresh(db_lesson)
    return db_lesson


@lesson_router.delete("/{lesson_id}", status_code=status.HTTP_200_OK)
async def delete_lesson(lesson_id: int, db: DBSessionDep, user: CurrentUserDep):
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    db_lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not db_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found"
        )
    course = db.query(Course).filter(Course.id == db_lesson.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {db_lesson.course_id} not found"
        )
    if course.author_id != user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Siz faqat ozingizni kurslaringizdagi darslarni o'chirishingiz mumkin"
        )
    db.delete(db_lesson)
    db.commit()

    return {"message": f"Lesson with id {lesson_id} has been deleted successfully"}