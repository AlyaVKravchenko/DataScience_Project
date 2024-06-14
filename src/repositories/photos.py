from select import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import PhotoModel
from src.models.users import UserModel


class PhotoRepo:

    def __init__(self, db):
        self.db: AsyncSession = db

    async def add_photo(self, user: UserModel, public_id: str, photo_url: str, description: str) -> PhotoModel:
        new_photo = PhotoModel(
            public_id=public_id,
            image_url=photo_url,
            user_id=user.id,
            description=description
        )
        self.db.add(new_photo)
        await self.db.commit()
        await self.db.refresh(new_photo)
        return new_photo

    async def get_all_photos(self, skip: int, limit: int) -> list[PhotoModel]:
        stmt = select(PhotoModel).offset(skip).limit(limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_photo_from_db(self, photo_id: int):
        stmt = select(PhotoModel).filter_by(id=photo_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def delete_photo(self, photo: PhotoModel):
        await self.db.delete(photo)
        await self.db.commit()

    async def update_photo(self, photo: PhotoModel):
        await self.db.commit()
        await self.db.refresh(photo)
        return photo

    async def get_photo_object_with_params(self, skip: int, limit: int):
        stmt = (select(PhotoModel.id,
                       PhotoModel.image_url,
                       PhotoModel.description,
                       UserModel.username,
                       )
                .select_from(UserModel)
                .join(PhotoModel, isouter=True)
                .filter(PhotoModel.id.isnot(None))
                .group_by(PhotoModel.id,
                          UserModel.username,
                          PhotoModel.image_url,
                          PhotoModel.description,
                          )
                .offset(skip)
                .limit(limit))
        result = await self.db.execute(stmt)
        return result

    async def get_photo_page(self, photo_id: int, skip: int | None = None, limit: int | None = None):
        stmt = (select(PhotoModel.id,
                       PhotoModel.image_url,
                       PhotoModel.description,
                       UserModel.username,
                       )
                .select_from(UserModel)
                .join(PhotoModel, isouter=True)
                .filter(PhotoModel.id == photo_id)
                .group_by(PhotoModel.id,
                          UserModel.username,
                          PhotoModel.image_url,
                          PhotoModel.description,
                          ))
        result = await self.db.execute(stmt)
        return result.first()