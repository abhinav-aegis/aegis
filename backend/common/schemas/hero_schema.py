from backend.common.models.hero_model import HeroBase
from backend.common.models.team_model import TeamBase
from backend.common.utils.partial import optional
from uuid import UUID
from pydantic import field_validator


class IHeroCreate(HeroBase):
    @field_validator("age")
    def check_age(cls, value):
        if value < 0:
            raise ValueError("Invalid age")
        return value


# All these fields are optional
@optional()
class IHeroUpdate(HeroBase):
    pass


class IHeroRead(HeroBase):
    id: UUID


class IHeroReadWithTeam(IHeroRead):
    team: TeamBase | None
