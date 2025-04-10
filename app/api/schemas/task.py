from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: UUID
    is_completed: Optional[bool] = False
    score: Optional[int] = Field(default=0, ge=0, le=10)


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class TaskScoreInput(BaseModel):
    score: int = Field(..., ge=0, le=10)


class TaskResponse(TaskBase):
    id: UUID
    created_at: int
    updated_at: int
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        orm_mode = True
