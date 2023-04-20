from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_superuser, current_user
from app.crud import charity_projects_crud, donations_crud
from app.models import User
from app.schemas.donation import (
    DonationBase, DonationCreate, DonationDB
)
from app.services.investing import investing, investing

router = APIRouter()


@router.get(
    '/',
    response_model=List[DonationDB],
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
        session: AsyncSession = Depends(get_async_session),
):
    """
    Только для суперюзеров.
    Возвращает список всех пожертвований.
    """
    all_donations = await donations_crud.get_multi(session)
    return all_donations


@router.get(
    '/my',
    response_model=List[DonationBase],
    response_model_exclude={'user_id'},
)
async def get_my_donations(
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user)
):
    """
    Вернуть список пожертвований пользователя,
    выполняющего запрос.
    """
    donations = await donations_crud.get_by_user(
        session=session, user=user
    )
    return donations


@router.post(
    '/',
    response_model=DonationBase,
    response_model_exclude_none=True,
)
async def create_donation(
        donation: DonationCreate,
        session: AsyncSession = Depends(get_async_session),
        user: User = Depends(current_user),
):
    """Сделать пожертвование."""
    new_donation = await donations_crud.create(
        donation,
        session,
        user,
        with_commit=False
    )
    not_full_projects = (
        await charity_projects_crud.get_not_full_objects(
            session=session
        )
    )
    session.add_all(
        investing(
            new_donation,
            not_full_projects,
        )
    )
    await session.commit()
    await session.refresh(new_donation)
    return new_donation
