from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import charity_projects_crud
from app.services.google_api import (
    create_table, spreadsheets_create,
    spreadsheets_update_value, set_user_permissions
)
from fastapi import HTTPException

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
    try:
        projects_by_completion_rate = (
            await charity_projects_crud.get_projects_by_completion_rate(session)
        )
        table_values, response = create_table(projects_by_completion_rate)
        spreadsheet_id = await spreadsheets_create(
            wrapper_services, table_values)
        await set_user_permissions(spreadsheet_id, wrapper_services)
        await spreadsheets_update_value(spreadsheet_id,
                                        table_values,
                                        wrapper_services)
    except OverflowError:
        raise HTTPException(
            status_code=500,
            detail='Таблица таблица переполненна данными'
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail='Проблемы на сервере, проверьте данные для google-api'
        )
    return response
