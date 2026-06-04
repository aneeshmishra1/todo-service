from typing import Annotated
from fastapi import Depends, HTTPException, Path, APIRouter
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.config import settings
from app.db.dependencies import get_db
from app.models.models import Todos
import logging

from app.schemas.user_schema import CurrentUser
from app.security.jwt_bearer import JWTBearer

logger = logging.getLogger(__name__)
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
router = APIRouter()

db_dependency = Annotated[AsyncSession, Depends(get_db)]
auth = JWTBearer()


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=500)
    priority: int = Field(0, ge=0, le=5)
    completed: bool


@router.get("/")
async def read_all(db: db_dependency, current_user: CurrentUser = Depends(auth)):
    logger.info("read_all_operation_started")
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    result = await db.execute(select(Todos).where(Todos.owner_id == current_user.user_id))
    return result.scalars().all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int, current_user: CurrentUser = Depends(auth)):
    logger.info("read_todo_operation_started")
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    result = await db.execute(select(Todos).filter(Todos.id == todo_id, Todos.owner_id == current_user.user_id))
    todo_model = result.scalar_one_or_none()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail='Todo not found')


@router.post("/todo/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest,
                      current_user: CurrentUser = Depends(auth)):
    logger.info("create_todo_operation_started")
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    todo_model = Todos(**todo_request.model_dump(), owner_id=current_user.user_id)
    db.add(todo_model)
    await db.commit()
    await db.refresh(todo_model)
    logger.info("create_todo_operation_ended")
    return {"message": "Todo created"}


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency,
                      todo_id: int,
                      todo_request: TodoRequest,
                      current_user: CurrentUser = Depends(auth)):
    logger.info("update_todo_operation_started")
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    result = await db.execute(
        select(Todos).where(
            Todos.id == todo_id,
            Todos.owner_id == current_user.user_id
        )
    )

    todo_model = result.scalar_one_or_none()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.completed = todo_request.completed

    db.add(todo_model)
    await db.commit()
    logger.info("update_todo_operation_ended")
    return {"message": "Todo updated"}


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(ge=0),
                      current_user: CurrentUser = Depends(auth)):
    logger.info("delete_todo_operation_started")
    if current_user.user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed')
    result = await db.execute(
        select(Todos).where(
            Todos.id == todo_id,
            Todos.owner_id == current_user.user_id
        )
    )
    todo_model = result.scalar_one_or_none()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    await db.delete(todo_model)
    await db.commit()
    logger.info("delete_todo_operation_ended")
    return {"message": "Todo deleted"}
