from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import auth, crud, schemas
from app.database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Todo API", version="1.0.0")


@app.post("/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_email(db, user.email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    return crud.create_user(db, user)


@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, form_data.username)
    if user is None or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return schemas.Token(access_token=auth.create_access_token(subject=user.email))


@app.post("/todos", response_model=schemas.TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(
    todo: schemas.TodoCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    return crud.create_todo(db, todo, owner_id=current_user.id)


@app.get("/todos", response_model=schemas.TodoListResponse)
def list_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    completed: Optional[bool] = None,
    q: Optional[str] = Query(None, description="Search in title/description"),
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    items, total = crud.list_todos(
        db, owner_id=current_user.id, skip=skip, limit=limit, completed=completed, q=q
    )
    return schemas.TodoListResponse(total=total, skip=skip, limit=limit, items=items)


@app.get("/todos/{todo_id}", response_model=schemas.TodoResponse)
def get_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    db_todo = crud.get_todo(db, todo_id, owner_id=current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return db_todo


@app.put("/todos/{todo_id}", response_model=schemas.TodoResponse)
def update_todo(
    todo_id: int,
    todo: schemas.TodoUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    db_todo = crud.get_todo(db, todo_id, owner_id=current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    return crud.update_todo(db, db_todo, todo)


@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(
    todo_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth.get_current_user),
):
    db_todo = crud.get_todo(db, todo_id, owner_id=current_user.id)
    if db_todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found")
    crud.delete_todo(db, db_todo)
    return None
