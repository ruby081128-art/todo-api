import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import PriorityEnum


class TodoBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime.date] = None
    priority: PriorityEnum = PriorityEnum.medium
    tags: list[str] = Field(default_factory=list)


class TodoCreate(TodoBase):
    pass


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime.date] = None
    priority: Optional[PriorityEnum] = None
    tags: Optional[list[str]] = None


class TodoResponse(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class TodoListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: list[TodoResponse]
