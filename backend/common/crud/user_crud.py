from backend.common.schemas.media_schema import IMediaCreate
from backend.common.schemas.user_schema import IUserCreate, IUserUpdate
from backend.common.models.user_model import User
from backend.common.models.media_model import Media
from backend.common.models.image_media_model import ImageMedia
from backend.common.core.security import verify_password, get_password_hash
from pydantic.networks import EmailStr
from backend.common.crud.base_crud import CRUDBase
from sqlmodel import select
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession


class CRUDUser(CRUDBase[User, IUserCreate, IUserUpdate]):
    async def get_by_email(
        self, *, email: str, db_session: AsyncSession | None = None
    ) -> User | None:
        db_session = db_session or super().get_db_session()
        users = await db_session.execute(select(User).where(User.email == email))
        return users.scalar_one_or_none()

    async def get_by_id_active(self, *, id: UUID) -> User | None:
        user = await super().get(id=id)
        if not user:
            return None
        if user.is_active is False:
            return None

        return user

    async def create_with_role(
        self, *, obj_in: IUserCreate, db_session: AsyncSession | None = None
    ) -> User:
        db_session = db_session or super().get_db_session()
        db_obj = User.model_validate(obj_in)
        db_obj.hashed_password = get_password_hash(obj_in.password)
        db_session.add(db_obj)
        await db_session.commit()
        await db_session.refresh(db_obj)
        return db_obj

    # async def update_is_active(
    #     self, *, db_obj: list[User], obj_in: int | str | dict[str, Any]
    # ) -> User | None:
    #     response = None
    #     db_session = super().get_db_session()
    #     for x in db_obj:
    #         x.is_active = obj_in.is_active
    #         db_session.add(x)
    #         await db_session.commit()
    #         await db_session.refresh(x)
    #         response.append(x)
    #     return response

    async def authenticate(self, *, email: EmailStr, password: str) -> User | None:
        user = await self.get_by_email(email=email)
        if not user or not user.hashed_password:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_photo(
        self,
        *,
        user: User,
        image: IMediaCreate,
        heigth: int,
        width: int,
        file_format: str,
    ) -> User:
        db_session = super().get_db_session()
        user.image = ImageMedia(
            media=Media.model_validate(image),
            height=heigth,
            width=width,
            file_format=file_format,
        )
        db_session.add(user)
        await db_session.commit()
        await db_session.refresh(user)
        return user

    async def remove(
        self, *, id: UUID | str, db_session: AsyncSession | None = None
    ) -> User:
        db_session = db_session or super().get_db_session()
        response = await db_session.execute(
            select(self.model).where(self.model.id == id)
        )
        obj = response.scalar_one()

        await db_session.delete(obj)
        await db_session.commit()
        return obj


user = CRUDUser(User)
