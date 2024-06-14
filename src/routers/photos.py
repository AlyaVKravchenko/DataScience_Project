from copy import deepcopy
from typing import Annotated

from fastapi import (APIRouter, Depends, HTTPException, Path, Query,
                     status)
from sqlalchemy.ext.asyncio import AsyncSession

# config
from src.conf import messages
from src.dependencies.database import get_db
# models
from src.models.users import Roles, UserModel
# schemas
from src.schemas.photos import (ImageResponseAfterCreateSchema,
                                ImageResponseAfterUpdateSchema, ImageSchema)

# services
from src.services.auth import auth_service
from src.services.cloudinary import CloudinaryService
from src.services.photos import PhotoService
from src.services.roles import RoleChecker

from src.schemas.unified import ImagePageResponseShortSchema, ImagePageResponseFullSchema


# routers
router_photos = APIRouter(prefix="/photos", tags=["Photos"])


@router_photos.get(
    "/",
    response_model=list[ImagePageResponseShortSchema],
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def show_photos(
        limit: Annotated[int, Query(description="Limit photos per page", ge=4, le=20)] = 4,
        skip: Annotated[int, Query(description="Skip number of photos", ge=0)] = 0,
        db: AsyncSession = Depends(get_db),
):
    """
    Show all photos. Pagination in query parameters:
        limit = limit photos per page
        skip = skip images from previous pages.
            Example: when limit = 10 photos per page,
            for the 3d page skip = 20.

    Show for all users, unregistered too
    """
    photos = await PhotoService(db).get_all_photo_per_page(skip=skip, limit=limit)
    return photos


@router_photos.get(
    "/{photo_id}",
    response_model=ImagePageResponseFullSchema,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def show_photo(
        photo_id: Annotated[int, Path(title="Photo ID", ge=1)],
        limit: Annotated[
            int, Query(description="Limit comments per page", ge=1, le=50)
        ] = 20,
        skip: Annotated[int, Query(description="Skip comments for next page", ge=0)] = 0,
        db: AsyncSession = Depends(get_db),
):
    """
    Show photo by id with comments if it is.
    Limit and skip in query parameters is for comments pagination.

    Additional undocumented functionality: if limit = 1,
    skip shows specific comment. (do not use as hardcoded url for comment)

    Show for all users, unregistered too
    """
    photo = await PhotoService(db).get_one_photo_page(photo_id, skip, limit)
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    return photo


@router_photos.post(
    "/",
    response_model=ImageResponseAfterCreateSchema,
    dependencies=None,
    status_code=status.HTTP_201_CREATED,
)
async def upload_photo(
        body: ImageSchema = Depends(),
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(auth_service.get_current_user),
):
    """
    Upload photos. Description and tags are optional.
    Only 5 tags accepted with ,(coma) separator.

    Only for registered users.
    """

    # Validate photo
    await PhotoService(db).validate_photo(body.file)


    # Upload photo and get url
    photo_cloud_url, public_id = CloudinaryService().upload_photo(
        body.file, current_user
    )
    # Add new_photo to db
    # Without deepcopy(or copy), new_photo isn't returned. I don't know why.
    new_photo = deepcopy(
        await PhotoService(db).add_photo(
            current_user, public_id, photo_cloud_url, body.description
        )
    )
    return new_photo


@router_photos.put(
    "/{photo_id}",
    response_model=ImageResponseAfterUpdateSchema,
    dependencies=None,
    status_code=status.HTTP_200_OK,
)
async def update_photo(
        photo_id: Annotated[int, Path(description="Photo ID", ge=1)],
        select: Annotated[
            str, Query(description="Choose action", enum=["photo", "comment"])
        ] = "photo",
        object_id: Annotated[int, Query(description="Choose object ID", ge=1)] = None,
        db: AsyncSession = Depends(get_db),
        current_user: UserModel = Depends(auth_service.get_current_user),
):
    """
    Change photo description.

    Only for registered users.
    Add - check if admin|moderator|owner
    """
    photo = await PhotoService(db).get_photo_exists(photo_id)
    # if no photo exists - nothing to edit
    if not photo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.PHOTO_NOT_FOUND
        )
    # Get user role
    admin_moderator_check = await RoleChecker(
        [Roles.admin, Roles.users]
    ).check_admin_or_user(user_id=current_user.id, db=db)

    if select == "photo":
        # photo owner or admin/moderator check
        if photo.user_id == current_user.id or admin_moderator_check is not None:
            edited_photo = await PhotoService(db).update_photo(photo)
            return edited_photo
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=messages.NO_EDIT_RIGHTS
            )

