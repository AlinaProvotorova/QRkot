from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_projects_crud
from app.models import CharityProject

DETAIL_CLOSE_PROJECT = "Закрытый проект нельзя редактировать!"
DETAIL_DELETE_PROJECT = (
    "В проект были внесены средства, не подлежит удалению!"
)
DETAIL_NAME_DUPLICATE = 'Проект с таким именем уже существует!'
DETAIL_PROJECT_EXISTS = "Проект не найден!"
DETAIL_SUM_PROJECT = (
    "Нельзя установить требуемую сумму меньше уже вложенной"
)


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
            detail=DETAIL_NAME_DUPLICATE,
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
            detail=DETAIL_PROJECT_EXISTS
        )
    return charity_project


def check_update_project(charity_project, obj_in):
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=400,
            detail=DETAIL_CLOSE_PROJECT
        )
    if obj_in.full_amount is not None:
        if charity_project.invested_amount > obj_in.full_amount:
            raise HTTPException(
                status_code=422,
                detail=DETAIL_SUM_PROJECT
            )


def check_delete_project(charity_project):
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=400,
            detail=DETAIL_DELETE_PROJECT
        )
