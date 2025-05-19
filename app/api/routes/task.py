from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from typing import List, Optional
from app.models.user import User
from app.core.locale import get_message
from app.api.dependencies import get_current_user, get_current_active_superuser
from app.api.routes.user import get_user_or_404

from app.api.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskScoreInput,
)
from app.models.task import Task
from app.utils.db import get_db, fetch_one, fetch_many

router = APIRouter(prefix="/tasks", tags=["Tasks"], dependencies=[Depends(get_current_user)])


async def get_task_or_404(db: AsyncSession, task_id: UUID, request: Request) -> Task:
    task = await fetch_one(db, Task, id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail=get_message("job_not_found", request))
    return task


# ✅ Tạo task
@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(request: Request, task_in: TaskCreate, db: AsyncSession = Depends(get_db)):
    user = await get_user_or_404(task_in.user_id, db, request)

    task = Task(**task_in.model_dump())

    task.created_by = str(user.id)
    task.updated_by = str(user.id)

    db.add(task)

    await db.commit()
    await db.refresh(task)
    return task


# ✅ Lấy danh sách task
@router.get("/", response_model=List[TaskResponse])
async def list_tasks(
        db: AsyncSession = Depends(get_db),
        page_number: int = Query(1, ge=0),
        page_size: int = Query(10, gt=0),
        task_id: Optional[str] = Query(None),
        title: Optional[str] = Query(None),
        description: Optional[str] = Query(None),
        user_id: Optional[str] = Query(None),
        is_completed: Optional[bool] = Query(None),
        score: Optional[int] = Query(None, ge=0, le=10),
        current_user: User = Depends(get_current_user),
):
    filters = []
    if task_id is not None:
        try:
            parsed_task_id = UUID(task_id)
            filters.append(Task.id == parsed_task_id)
        except ValueError:
            return []  # task_id không hợp lệ
    if title is not None:
        # Sử dụng ilike để hỗ trợ tìm kiếm không phân biệt chữ hoa chữ thường
        filters.append(Task.title.ilike(f"%{title}%"))
    if description is not None:
        filters.append(Task.description.ilike(f"%{description}%"))

    if not current_user.is_superuser:
        # Người dùng thường: chỉ xem task của chính mình
        filters.append(Task.user_id == current_user.id)
    else:
        # Superuser: có thể lọc theo user_id
        if user_id is not None:
            try:
                valid_uuid = UUID(user_id)
                filters.append(Task.user_id == valid_uuid)
            except ValueError:
                return []

    if is_completed is not None:
        filters.append(Task.is_completed == is_completed)
    if score is not None:
        filters.append(Task.score == score)

    if page_number == 0:
        offset = None
        limit = None
    else:
        offset = (page_number - 1) * page_size
        limit = page_size

    result = await fetch_many(
        db=db,
        model=Task,
        filters=filters,
        limit=limit,
        offset=offset
    )

    return result


# ✅ Lấy task theo ID
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(request: Request, task_id: UUID, db: AsyncSession = Depends(get_db)):
    task = await get_task_or_404(db, task_id, request)
    return task


# ✅ Cập nhật task
@router.put("/{task_id}", response_model=TaskResponse, dependencies=[Depends(get_current_active_superuser)])
async def update_task(request: Request, task_id: UUID, task_in: TaskUpdate, db: AsyncSession = Depends(get_db)):
    task = await get_task_or_404(db, task_id, request)

    for key, value in task_in.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


# ✅ Xóa task
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_current_active_superuser)])
async def delete_task(request: Request, task_id: UUID, db: AsyncSession = Depends(get_db)):
    task = await get_task_or_404(db, task_id, request)

    await db.delete(task)
    await db.commit()
    return


# ✅ Hoàn thành task
@router.put("/complete/{task_id}", response_model=TaskResponse)
async def complete_task(request: Request, task_id: UUID, db: AsyncSession = Depends(get_db),
                        current_user: User = Depends(get_current_user)):
    task = await get_task_or_404(db, task_id, request)

    if current_user.id != task.user_id:
        raise HTTPException(status_code=404, detail=get_message("job_not_assigned_to_you", request))

    task.is_completed = True

    await db.commit()
    await db.refresh(task)
    return task


# ✅ Chấm điểm task (yêu cầu is_completed = True)
@router.put("/score/{task_id}", response_model=TaskResponse, dependencies=[Depends(get_current_active_superuser)])
async def score_task(
        request: Request,
        task_id: UUID,
        input_data: TaskScoreInput,
        db: AsyncSession = Depends(get_db),
):
    task = await get_task_or_404(db, task_id, request)

    if not task.is_completed:
        raise HTTPException(status_code=400, detail=get_message("job_not_completed_no_review", request))

    task.score = input_data.score
    await db.commit()
    await db.refresh(task)
    return task
