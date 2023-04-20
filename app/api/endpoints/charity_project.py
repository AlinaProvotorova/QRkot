from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    charity_project_exists, check_delete_project,
    check_name_duplicate, check_update_project
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_projects_crud, donations_crud
from app.schemas.charity_project import (
    CharityProjectCreate, CharityProjectDB, CharityProjectUpdate
)
from app.services.investing import investing

router = APIRouter()


@router.get(
    '/',
    response_model=List[CharityProjectDB],
    response_model_exclude_none=True,
)
async def get_all_meeting_rooms(
        session: AsyncSession = Depends(get_async_session),
):
    """Возвращает список всех проектов."""
    all_projects = await charity_projects_crud.get_multi(session)
    return all_projects


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_new_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session)
):
    """
    Только для суперюзеров.
    Создаёт благотворительный проект.
    """
    await check_name_duplicate(charity_project.name, session)
    new_charity_project = await charity_projects_crud.create(
        charity_project,
        session,
        with_commit=False
    )
    not_full_donations = await donations_crud.get_not_full_objects(
        session=session
    )
    session.add_all(
        investing(
            new_charity_project,
            not_full_donations,
        )
    )
    await session.commit()
    await session.refresh(new_charity_project)
    return new_charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
        project_id: int,
        obg_in: CharityProjectUpdate,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Закрытый проект нельзя редактировать;
    нельзя установить требуемую сумму меньше уже вложенной.
    """
    charity_project = await charity_project_exists(
        project_id, session
    )
    check_update_project(charity_project, obg_in)
    if obg_in.name is not None:
        await check_name_duplicate(obg_in.name, session)
    charity_project = await charity_projects_crud.update(
        charity_project, obg_in, session
    )
    return charity_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)],
)
async def remove_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Удаляет проект.
    Нельзя удалить проект, в который уже были инвестированы средства,
    его можно только закрыть.
    """
    charity_project = await charity_project_exists(
        project_id, session
    )
    check_delete_project(charity_project)
    charity_project = await charity_projects_crud.remove(
        charity_project, session
    )
    return charity_project
