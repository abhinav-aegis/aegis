from backend.common.models.media_model import MediaBase
from backend.common.utils.partial import optional
from uuid import UUID


class IMediaCreate(MediaBase):
    pass


# All these fields are optional
@optional()
class IMediaUpdate(MediaBase):
    pass


class IMediaRead(MediaBase):
    id: UUID | str
    link: str | None = None
