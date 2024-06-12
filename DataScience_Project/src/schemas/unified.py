from typing import List, Optional


# schemas
from src.schemas.photos import ImageBaseResponseSchema


class ImagePageResponseShortSchema(ImageBaseResponseSchema):
    username: Optional[str] | None


class ImagePageResponseFullSchema(ImagePageResponseShortSchema):
    username: Optional[str] | None


