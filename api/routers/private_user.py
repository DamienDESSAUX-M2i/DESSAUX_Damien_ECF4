from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.dependencies.auth import get_current_user, require_roles
from api.models.user import User, UserRole
from api.schemas.user import UserPublic
from api.schemas.utils import APIResponse, MessageResponse
from api.services.user import delete_user_by_id, get_all_users
from api.utils.logger import get_logger

logger = get_logger()

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=APIResponse[UserPublic])
def read_me(
    current_user: User = Depends(get_current_user),
) -> APIResponse[UserPublic]:
    logger.info(
        f"Fetch current user : user_id={current_user.id}, username={current_user.name}",
    )

    user_data = UserPublic(
        name=current_user.name,
        role=current_user.role,
        is_active=current_user.is_active,
    )
    return APIResponse(
        status=True,
        data=user_data,
        message="User logged in successfully recovered.",
        timestamp=datetime.now(timezone.utc),
    )


@router.get("/", response_model=APIResponse[List[UserPublic]])
def list_users(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> APIResponse[List[UserPublic]]:
    logger.info(
        f"List users requested : admin_id={current_user.id}",
    )

    users = get_all_users(db)
    users_data = [
        UserPublic(
            name=user.name,
            role=user.role,
            is_active=user.is_active,
        )
        for user in users
    ]

    logger.info(f"Users retrieved : count={len(users_data)}")

    return APIResponse(
        status=True,
        data=users_data,
        message=f"{len(users_data)} users found.",
        timestamp=datetime.now(timezone.utc),
    )


@router.delete("/{user_id}", response_model=APIResponse[MessageResponse])
def admin_delete_user(
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: Session = Depends(get_db),
) -> APIResponse[MessageResponse]:
    logger.info(
        f"Delete user requested : target_user_id={user_id}",
    )

    if current_user.id == user_id:
        logger.warning("Admin attempted to delete themselves")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An administrator cannot delete themselves.",
        )

    deleted_user = delete_user_by_id(db, user_id)
    if deleted_user is None:
        logger.warning(
            f"Delete user failed: user not found : target_user_id={user_id}",
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    logger.info(
        f"User deleted successfully : deleted_user_id={deleted_user.id}, deleted_username={deleted_user.name}"
    )

    return APIResponse(
        status=True,
        data=MessageResponse(message=f"User {deleted_user.name} deleted."),
        message="User successfully deleted.",
        timestamp=datetime.now(timezone.utc),
    )
