import enum

from sqlalchemy import Boolean, Column, Date, DateTime, Enum, Integer, JSON, String, func

from app.database import Base


class PriorityEnum(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    description = Column(String, nullable=True)
    completed = Column(Boolean, nullable=False, default=False)
    due_date = Column(Date, nullable=True)
    priority = Column(Enum(PriorityEnum), nullable=False, default=PriorityEnum.medium)
    tags = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
