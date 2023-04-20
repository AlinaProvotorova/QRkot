from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base_crud import CRUDBase
from app.models.charity_project import CharityProject


class CRUDCharityProject(CRUDBase):

    async def get_project_id_by_name(
            self,
            project_name: str,
            session: AsyncSession,
    ) -> Optional[int]:
        db_room_id = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name
            )
        )
        return db_room_id.scalars().first()

    async def get_projects_by_completion_rate(
            self,
            session: AsyncSession
    ):
        db_obj = await session.execute(
            select(self.model).where(
                self.model.fully_invested == 1
            ).order_by(
                self.model.close_date - self.model.create_date
            )
        )
        return db_obj.scalars().all()


charity_projects_crud = CRUDCharityProject(CharityProject)
