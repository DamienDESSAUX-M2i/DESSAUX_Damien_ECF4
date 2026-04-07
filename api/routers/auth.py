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

router = APIRouter(prefix="/auth", tags=["Authentication"])


def generate_access_token(user: User) -> str:
    """Génère un JWT à partir d'une instance de User"""
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
    """Créer un nouvel utilisateur"""
    existing_user = get_user_by_name(db, payload.name)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ce nom d'utilisateur existe déjà.",
        )

    created_user = create_user(
        db=db,
        name=payload.name,
        password=payload.password,
        role=UserRole.USER,
    )

    return APIResponse(
        status=True,
        data=created_user,
        message="Utilisateur créé avec succès",
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/login", response_model=APIResponse[LoginResponse])
def login(
    payload: UserLogin, db: Session = Depends(get_db)
) -> APIResponse[LoginResponse]:
    """Authentifie l'utilisateur et retourne un JWT si valide"""
    settings = get_settings()

    user = get_user_by_name(db, payload.name)

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides.",
        )

    access_token = generate_access_token(user)

    response_data = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes,
        user=user,
    )

    return APIResponse(
        status=True,
        data=response_data,
        message="Connexion réussie",
        timestamp=datetime.now(timezone.utc),
    )


@router.post("/refresh", response_model=APIResponse[LoginResponse])
def refresh(
    current_user: User = Depends(get_current_user),
) -> APIResponse[LoginResponse]:
    """Génère un nouveau token pour l'utilisateur authentifié"""
    settings = get_settings()

    access_token = generate_access_token(current_user)

    response_data = LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes,
        user=current_user,
    )

    return APIResponse(
        status=True,
        data=response_data,
        message="Token rafraîchi avec succès",
        timestamp=datetime.now(timezone.utc),
    )
