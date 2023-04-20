from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_projects_crud
from app.models import CharityProject
from app.core.config import settings

detail_close_project = "Закрытый проект нельзя редактировать!"
detail_delete_project = "В проект были внесены средства, не подлежит удалению!"
detail_name_duplicate = 'Проект с таким именем уже существует!'
detail_project_exists = "Проект не найден!"
detail_sum_project = "Нельзя установить требуемую сумму меньше уже вложенной"
detail_size_for_sheet = "Данные таблицы превышают размер таблицы, нужно увеличить"


async def check_name_duplicate(
        charity_projects_name: str,
        session: AsyncSession
):
    room_id = await charity_projects_crud.get_project_id_by_name(
        charity_projects_name,
        session
    )
    if room_id is not None:
        raise HTTPException(
            status_code=400,
            detail=detail_name_duplicate,
        )


async def charity_project_exists(
        charity_project_id: int,
        session: AsyncSession
) -> CharityProject:
    charity_project = await charity_projects_crud.get(
        charity_project_id, session
    )
    if charity_project is None:
        raise HTTPException(
            status_code=404,
            detail=detail_project_exists
        )
    return charity_project


def check_update_project(charity_project, obj_in):
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail=detail_close_project
        )
    if obj_in.full_amount is not None:
        if charity_project.invested_amount > obj_in.full_amount:
            raise HTTPException(
                status_code=422,
                detail=detail_sum_project
            )


def check_delete_project(charity_project):
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail=detail_delete_project
        )


def check_size_for_sheet(row_count, column_count):
    if row_count > settings.ROW_COUNT or column_count > settings.COLUMN_COUNT:
        raise HTTPException(
            status_code=422,
            detail=detail_size_for_sheet
        )
