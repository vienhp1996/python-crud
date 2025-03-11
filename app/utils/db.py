from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Row, RowMapping
from typing import Any, List, Type, Sequence


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session


async def fetch_one(db: AsyncSession, model: Type[Any], **filters) -> Any:
    """
    Truy vấn và trả về 1 đối tượng dựa trên các điều kiện (filters) truyền vào.
    Nếu không tìm thấy, trả về None.
    """
    query = select(model).filter_by(**filters)
    result = await db.execute(query)
    return result.scalars().first()


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, List, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Any, List, Type


async def fetch_many(
        db: AsyncSession,
        model: Type[Any],
        filters: List[Any] = None,
        order_by: Any = None,
        limit: int = None,
        offset: int = None
) -> Sequence[Row[Any] | RowMapping | Any]:
    query = select(model)
    # Kiểm tra filters một cách rõ ràng
    if filters is not None and len(filters) > 0:
        query = query.filter(*filters)
    if order_by is not None:
        query = query.order_by(order_by)
    if limit is not None:
        query = query.limit(limit)
    if offset is not None:
        query = query.offset(offset)
    result = await db.execute(query)
    return result.scalars().all()


async def fetch_all(db: AsyncSession, model: Type[Any], **filters) -> Sequence[Row[Any] | RowMapping | Any]:
    """
    Truy vấn và trả về danh sách đối tượng từ model.
    Nếu có filters được cung cấp, áp dụng filter để thu hẹp kết quả.
    """
    query = select(model)
    if filters:
        query = query.filter_by(**filters)
    result = await db.execute(query)
    return result.scalars().all()
