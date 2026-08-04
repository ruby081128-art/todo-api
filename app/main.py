from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API", version="1.0.0")


@app.post("/todos", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return crud.create_todo(db, todo)


@app.get("/todos", response_model=schemas.TodoListResponse)
def list_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    completed: Optional[bool] = None,
    q: Optional[str] = Query(None, description="Search in title/description"),
    db: Session = Depends(get_db),
):
    items, total = crud.list_todos(db, skip=skip, limit=limit, completed=completed, q=q)
    return schemas.TodoListResponse(total=total, skip=skip, limit=limit, items=items)


@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = crud.get_todo(db, todo_id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return db_todo


@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(todo_id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)):
    db_todo = crud.get_todo(db, todo_id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return crud.update_todo(db, db_todo, todo)


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = crud.get_todo(db, todo_id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    crud.delete_todo(db, db_todo)
    return None
