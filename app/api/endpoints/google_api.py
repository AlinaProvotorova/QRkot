from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import charity_projects_crud
from app.services.google_api import spreadsheets_create, spreadsheets_update_value, set_user_permissions

router = APIRouter()


@router.post(
    '/',
    response_model=list[dict[str, str]],
    dependencies=[Depends(current_superuser)],
)
async def get_report(
        session: AsyncSession = Depends(get_async_session),
        wrapper_services: Aiogoogle = Depends(get_service)

):
    """Только для суперюзеров. Создает отчет в googlesheets"""
    projects_by_completion_rate = await charity_projects_crud.get_projects_by_completion_rate(session)
    projects_for_spreadsheet = []
    for model in projects_by_completion_rate:
        duration = model.close_date - model.create_date
        projects_for_spreadsheet.append(
            {
                "name": model.name,
                "duration": str(duration),
                "description": model.description
            }
        )
    spreadsheet_id = await spreadsheets_create(wrapper_services)
    await set_user_permissions(spreadsheet_id, wrapper_services)
    await spreadsheets_update_value(spreadsheet_id,
                                    projects_for_spreadsheet,
                                    wrapper_services)
    return projects_for_spreadsheet
