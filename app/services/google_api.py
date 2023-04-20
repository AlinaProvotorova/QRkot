from datetime import datetime

from aiogoogle import Aiogoogle
from app.core.config import settings
from app.api.validators import check_size_for_sheet


async def spreadsheets_create(
        wrapper_services: Aiogoogle

) -> str:
    now_date_time = datetime.now().strftime(settings.FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = settings.SPREADSHEET_BODY.copy()
    spreadsheet_body['properties']['title'] = spreadsheet_body['properties']['title'].format(now_date_time)
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheetid: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {'type': 'user',
                        'role': 'writer',
                        'emailAddress': settings.superuser_email}
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheetid,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        charity_projects_full: list,
        wrapper_services: Aiogoogle
) -> None:
    now_date_time = datetime.now().strftime(settings.FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')
    table_header = settings.TABLE_HEADER.copy()
    table_header[0][1] = table_header[0][1].format(now_date_time)
    table_values = [
        *table_header,
        *[[project['name'], project['duration'], project['description']]
          for project in charity_projects_full],
    ]
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    check_size_for_sheet(
        len((max(table_values, key=len))),
        len(table_values)
    )
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=settings.RANGE,
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
