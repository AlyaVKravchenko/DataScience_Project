from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.dependencies.database import get_db
from src.models.users import Roles, UserModel
from src.schemas.users import (UserUpdateAvatarSchema, UserMyResponseSchema, UserResponseExtendedSchema,
                               UserUpdateByAdminSchema, UserUpdateEmailSchema, UserAdminResponseSchema)
from src.services.auth import auth_service
from src.services.photos import PhotoService
from src.services.cloudinary import CloudinaryService
from src.services.roles import RoleChecker

router_users = APIRouter(prefix="/users", tags=["Users"])


@router_users.put(
    "/my_profile/email",
    response_model=UserMyResponseSchema,
    dependencies=None,
    status_code=None
)
async def update_email_current_user(
        body: UserUpdateEmailSchema = Depends(),
        current_user: UserModel = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    exist_user_by_email = await auth_service.get_user_by_email(body.email, db=db)
    if exist_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.EMAIL_IS_ALREADY_BUSY
        )

    if not auth_service.verify_password(body.confirm_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )

    if body.email:
        current_user = await auth_service.change_email(current_user.id, body.email, db)

    return current_user


@router_users.put(
    "/{username}",
    response_model=UserAdminResponseSchema,
    dependencies=[Depends(RoleChecker([Roles.admin]))],
)
async def update_user(
        username: str,
        body: UserUpdateByAdminSchema = Depends(),
        db: AsyncSession = Depends(get_db)
):
    """
    Method put for username only if admin.

    Show everything about user (excludes password), can change only: is_active, role
    """
    user = await auth_service.get_user_by_username(username, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.ACCOUNT_NOT_FOUND
        )
    user = await auth_service.update_user_by_admin(user.id, body, db)

    return user
