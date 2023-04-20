from typing import Optional
from pydantic import BaseSettings, EmailStr


class Settings(BaseSettings):
    app_title: str = 'Благотворительный фонд поддержки котиков QRKot'
    database_url: str = 'sqlite+aiosqlite:///./fastapi.db'
    secret: str = 'SECRET'
    superuser_email: Optional[EmailStr] = None
    superuser_password: Optional[str] = None
    # Переменные для Google API
    type: Optional[str] = None
    project_id: Optional[str] = None
    private_key_id: Optional[str] = None
    private_key: Optional[str] = None
    client_email: Optional[str] = None
    client_id: Optional[str] = None
    auth_uri: Optional[str] = None
    token_uri: Optional[str] = None
    auth_provider_x509_cert_url: Optional[str] = None
    client_x509_cert_url: Optional[str] = None
    email: Optional[str] = None

    FORMAT = "%Y/%m/%d %H:%M:%S"
    ROW_COUNT = 100
    COLUMN_COUNT = 10
    RANGE = f'R1C1:R{ROW_COUNT}C{COLUMN_COUNT}'
    SPREADSHEET_BODY = dict(
        properties=dict(
            title='Отчет от {}',
            locale='ru_RU',
        ),
        sheets=[dict(properties=dict(
            sheetType='GRID',
            sheetId=0,
            title='Лист1',
            gridProperties=dict(
                rowCount=ROW_COUNT,
                columnCount=COLUMN_COUNT,
            )
        ))]
    )
    TABLE_HEADER = [
        ['Отчет от', '{}'],
        ['Топ проектов по скорости закрытия'],
        ['Название проекта', 'Время сбора', 'Описание']
    ]

    class Config:
        env_file = '.env'


settings = Settings()
