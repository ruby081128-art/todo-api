from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models, schemas


def create_todo(db: Session, todo: schemas.TodoCreate) -> models.Todo:
    db_todo = models.Todo(**todo.model_dump())
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def get_todo(db: Session, todo_id: int) -> Optional[models.Todo]:
    return db.query(models.Todo).filter(models.Todo.id == todo_id).first()


def list_todos(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    completed: Optional[bool] = None,
    q: Optional[str] = None,
) -> tuple[list[models.Todo], int]:
    query = db.query(models.Todo)

    if completed is not None:
        query = query.filter(models.Todo.completed == completed)

    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(models.Todo.title.ilike(like), models.Todo.description.ilike(like))
        )

    total = query.count()
    items = query.order_by(models.Todo.id).offset(skip).limit(limit).all()
    return items, total


def update_todo(
    db: Session, db_todo: models.Todo, todo: schemas.TodoUpdate
) -> models.Todo:
    for field, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, field, value)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def delete_todo(db: Session, db_todo: models.Todo) -> None:
    db.delete(db_todo)
    db.commit()
