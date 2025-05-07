# routers/comment.py
from fastapi import APIRouter, status, HTTPException
from models.comment import Comment
from models.course import Lesson
from core.dependencies import DBSessionDep, CurrentUserDep
from schemas.comment import CommentOut, CommentCreate, CommentUpdate
from datetime import datetime

comment_router = APIRouter(
    prefix="/comment",
    tags=["comment"]
)


@comment_router.get("/", response_model=list[CommentOut])
async def get_comments(db: DBSessionDep, user: CurrentUserDep):
    """Get all comments for the authenticated user"""
    return db.query(Comment).filter(Comment.author_id == user.get("id")).all()


@comment_router.get("/lesson/{lesson_id}", response_model=list[CommentOut])
async def get_comments_by_lesson(lesson_id: int, db: DBSessionDep):
    """Get all comments for a specific lesson"""
    if not db.query(Lesson).filter(Lesson.id == lesson_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sizda bunday id {lesson_id} dars mavjud emas!"  # noqa
        )
    return db.query(Comment).filter(Comment.lesson_id == lesson_id).all()


@comment_router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
async def create_comment(
        comment: CommentCreate,
        db: DBSessionDep,
        user: CurrentUserDep
):
    """Create a new comment"""
    # Check if lesson exists
    if not db.query(Lesson).filter(Lesson.id == comment.lesson_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {comment.lesson_id} not found"
        )

    new_comment = Comment(
        lesson_id=comment.lesson_id,
        author_id=user.get("id"),
        text=comment.text,
        created_at=datetime.utcnow(),
    )

    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment


@comment_router.put("/{comment_id}", response_model=CommentOut)
async def update_comment(
        comment_id: int,
        comment: CommentUpdate,
        db: DBSessionDep,
        user: CurrentUserDep
):
    """Update a comment"""
    db_comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.author_id == user.get("id")  # Ensure user owns the comment
    ).first()

    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to edit it"
        )

    db_comment.text = comment.text

    db.commit()
    db.refresh(db_comment)
    return db_comment


@comment_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
        comment_id: int,
        db: DBSessionDep,
        user: CurrentUserDep
):
    """Delete a comment"""
    db_comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.author_id == user.get("id")  # Ensure user owns the comment
    ).first()

    if not db_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )

    db.delete(db_comment)
    db.commit()
    return None