from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.core.security import create_access_token, verify_password
from api.core.settings import get_settings
from api.dependencies.auth import get_current_user
from api.models.user import User, UserRole
from api.schemas.user import (
    LoginResponse,
    UserLogin,
    UserPublic,
    UserRegister,
)
from api.schemas.utils import APIResponse
from api.services.user import create_user, get_user_by_name
from api.utils.logger import get_logger

logger = get_logger()

router = APIRouter(prefix="/auth", tags=["Authentication"])


def generate_access_token(user: User) -> str:
    return create_access_token(
        data={
            "sub": user.name,
            "role": user.role.value,
        },
    )


@router.post(
    "/register",
    response_model=APIResponse[UserPublic],
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: UserRegister, db: Session = Depends(get_db)
) -> APIResponse[UserPublic]:
    logger.info(f"User registration attempt : username={payload.name}")

    existing_user = get_user_by_name(db, payload.name)
    if existing_user:
        logger.warning(
            "Registration failed: username already exists : username={payload.name}",
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"The name {payload.name} already exists.",
        )

    created_user = create_user(
        db=db,
        name=payload.name,
        password=payload.password,
        role=UserRole.USER,
    )

    logger.info(
        f"User registered successfully : user_id={created_user.id}, username={created_user.name}",
    )

    return APIResponse(
        status=True,
        data=created_user,
        message="User created successfully",
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/login", response_model=APIResponse[LoginResponse])
def login(
    payload: UserLogin, db: Session = Depends(get_db)
) -> APIResponse[LoginResponse]:
    logger.info(f"Login attempt : username={payload.name}")

    settings = get_settings()

    user = get_user_by_name(db, payload.name)

    if not user or not verify_password(payload.password, user.password_hash):
        logger.warning(
            f"Login failed: invalid credentials : username={payload.name}",
        )

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )

    access_token = generate_access_token(user)

    logger.info(
        f"Login successful : user_id={user.id}, username={user.name}",
    )

    response_data = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes,
        user=user,
    )

    return APIResponse(
        status=True,
        data=response_data,
        message="Connexion success",
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/refresh", response_model=APIResponse[LoginResponse])
def refresh(
    current_user: User = Depends(get_current_user),
) -> APIResponse[LoginResponse]:
    logger.info(
        f"Token refresh requested : user_id={current_user.id}, username={current_user.name}",
    )

    settings = get_settings()

    access_token = generate_access_token(current_user)

    logger.info(
        f"Token refreshed successfully : user_id={current_user.id}",
    )

    response_data = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes,
        user=current_user,
    )

    return APIResponse(
        status=True,
        data=response_data,
        message="Token successfully refreshed",
        timestamp=datetime.now(timezone.utc),
    )
