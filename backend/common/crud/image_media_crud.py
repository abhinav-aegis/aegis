from backend.common.crud.base_crud import CRUDBase
from backend.common.models.image_media_model import ImageMedia
from backend.common.schemas.image_media_schema import IImageMediaCreate, IImageMediaUpdate


class CRUDImageMedia(CRUDBase[ImageMedia, IImageMediaCreate, IImageMediaUpdate]):
    pass


image = CRUDImageMedia(ImageMedia)
