from io import BytesIO
from uuid import UUID

from fastapi import HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.photos import PhotoModel
from src.models.users import UserModel
from src.repositories.photos import PhotoRepo
from src.repositories.users import UserRepo


class PhotoService:
    def __init__(self, db: AsyncSession):
        self.repo = PhotoRepo(db=db)

    async def get_photo_exists(self, photo_id: int):
        result = await self.repo.get_photo_from_db(photo_id)
        return result

    async def add_photo(self, user: UserModel, public_id: str, photo_url: str, description: str) -> PhotoModel:
        new_photo = await self.repo.add_photo(user, public_id, photo_url, description)

        return new_photo

    async def get_all_photos(self, skip: int, limit: int) -> list[PhotoModel]:
        photos = await self.repo.get_all_photos(skip, limit)
        return photos

    async def delete_photo(self, photo: PhotoModel) -> None:
        await self.repo.delete_photo(photo)

    async def update_photo(self, photo: PhotoModel) -> PhotoModel:
        photo = await self.repo.update_photo(photo)
        return photo

    async def get_all_photo_per_page(self, skip: int, limit: int):
        query = await self.repo.get_photo_object_with_params(skip, limit)
        result = []
        for photo in query:
            result.append(photo._asdict())
        return result

    async def get_one_photo_page(self, photo_id: int, skip: int, limit: int):
        result = await self.repo.get_photo_page(photo_id)
        if result is not None:
            result = result._asdict()
        return result

    async def get_photo_count(self, user_id: UUID):
        count = await self.repo.get_picture_count(user_id)
        return count
