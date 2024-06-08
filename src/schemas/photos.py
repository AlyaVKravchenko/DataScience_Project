from datetime import datetime
from typing import List, Optional

from fastapi import File, UploadFile
from pydantic import BaseModel, Field


class ImageUpdateSchema(BaseModel):
    description: Optional[str] = Field(min_length=3, max_length=255)


class ImageSchema(ImageUpdateSchema):
    file: UploadFile = File()
    tags: Optional[str] = None


class ImageBaseResponseSchema(BaseModel):
    id: int
    image_url: str | None
    description: Optional[str] | None


class ImageResponseAfterUpdateSchema(ImageBaseResponseSchema):
    updated_at: datetime


class ImageResponseAfterCreateSchema(ImageResponseAfterUpdateSchema):
    public_id: str


