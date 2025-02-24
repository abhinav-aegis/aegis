from backend.common.schemas.team_schema import ITeamCreate, ITeamUpdate
from backend.common.crud.base_crud import CRUDBase
from backend.common.models.team_model import Team
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional

class CRUDTeam(CRUDBase[Team, ITeamCreate, ITeamUpdate]):
    async def get_team_by_name(
        self, *, name: str, db_session: AsyncSession | None = None
    ) -> Optional[Team]:
        db_session = db_session or super().get_db_session()
        team = await db_session.execute(select(Team).where(Team.name == name))
        return team.scalar_one_or_none()


team = CRUDTeam(Team)
