import copy
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings

FORMAT = "%Y/%m/%d %H:%M:%S"
NOW_DATE_TIME = datetime.now().strftime(FORMAT)
TABLE_HEADER = [
    ['Отчет от', '{}'],
    ['Топ проектов по скорости закрытия'],
    ['Название проекта', 'Время сбора', 'Описание']
]
SPREADSHEET_BODY = dict(
    properties=dict(
        title='Отчет от {}',
        locale='ru_RU',
    ),
    sheets=[dict(
        properties=dict(
            sheetType='GRID',
            sheetId=0,
            title='Лист1',
            gridProperties=dict(
                rowCount=1,  # устанавливаются при создании таблицы
                columnCount=1,  # устанавливаются при создании таблицы
            )
        ))]
)


def create_table(charity_projects_full: list):
    projects_for_response = []
    for model in charity_projects_full:
        projects_for_response.append(
            {
                "name": model.name,
                "duration": str(model.close_date - model.create_date),
                "description": model.description
            }
        )
    table_header = copy.deepcopy(TABLE_HEADER)
    table_header[0][1] = table_header[0][1].format(NOW_DATE_TIME)
    table_values = [
        *table_header,
        *[[project['name'], project['duration'], project['description']]
          for project in projects_for_response],
    ]

    return table_values, projects_for_response


async def spreadsheets_create(
        wrapper_services: Aiogoogle,
        table_values: list[dict[str, str]]
) -> str:
    service = await wrapper_services.discover('sheets', 'v4')
    spreadsheet_body = copy.deepcopy(SPREADSHEET_BODY)
    spreadsheet_body['properties']['title'] = (
        spreadsheet_body['properties']['title'].format(NOW_DATE_TIME))
    grid_properties = spreadsheet_body['sheets'][0]['properties']['gridProperties']
    grid_properties['rowCount'] = len(table_values)
    grid_properties['columnCount'] = len((max(table_values, key=len)))
    if (
            grid_properties['rowCount'] > 500 or
            grid_properties['columnCount'] > 18000
    ):  # проверка ограничения гугл-таблиц на количество строк и столбцов
        raise ValueError("Данные занимают больше 500 строк или 18000 столбцов")
    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(json=spreadsheet_body)
    )
    spreadsheet_id = response['spreadsheetId']
    return spreadsheet_id


async def set_user_permissions(
        spreadsheet_id: str,
        wrapper_services: Aiogoogle
) -> None:
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.superuser_email
    }
    service = await wrapper_services.discover('drive', 'v3')
    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,
            json=permissions_body,
            fields="id"
        ))


async def spreadsheets_update_value(
        spreadsheet_id: str,
        table_values: list[dict[str, str]],
        wrapper_services: Aiogoogle
) -> list[dict[str, str]]:
    service = await wrapper_services.discover('sheets', 'v4')
    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }
    row_count = len(table_values)
    column_count = len((max(table_values, key=len)))
    await wrapper_services.as_service_account(
        service.spreadsheets.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'R1C1:R{row_count}C{column_count}',
            valueInputOption='USER_ENTERED',
            json=update_body
        )
    )
    return table_values
