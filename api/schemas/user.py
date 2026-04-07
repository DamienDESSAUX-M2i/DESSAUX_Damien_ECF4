from pydantic import BaseModel, ConfigDict, Field

from api.models.user import UserRole


class UserRegister(BaseModel):
    """Data required to register a new user."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        title="Username",
        description="Unique username used for authentication",
        examples=["john_doe"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        title="Password",
        description="User password (plain text before hashing)",
        examples=["Password123!"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "john_doe",
                "password": "Password123!",
            }
        }
    )


class UserLogin(BaseModel):
    """Data required to authenticate a user."""

    name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        title="Username",
        description="Username used to authenticate",
        examples=["john_doe"],
    )
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        title="Password",
        description="User password",
        examples=["Password123!"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "john_doe",
                "password": "Password123!",
            }
        }
    )


class UserPublic(BaseModel):
    """Public representation of a user."""

    name: str = Field(
        ...,
        title="Username",
        description="Unique username",
        examples=["john_doe"],
    )
    role: UserRole = Field(
        ...,
        title="User role",
        description="Role assigned to the user (e.g. user or admin)",
        examples=["user"],
    )
    is_active: bool = Field(
        ...,
        title="Active status",
        description="Indicates whether the user account is active",
        examples=[True],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "name": "john_doe",
                "role": "user",
                "is_active": True,
            }
        },
    )


class TokenResponse(BaseModel):
    """Response returned after authentication or token refresh."""

    access_token: str = Field(
        ...,
        title="Access token",
        description="JWT token used for authenticated requests",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        title="Token type",
        description="Type of token used for authentication",
        examples=["bearer"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
            }
        }
    )


class LoginResponse(TokenResponse):
    """
    Extended login response including user information.
    """

    user: UserPublic = Field(
        ...,
        title="User",
        description="Authenticated user information",
    )
    expires_in: int = Field(
        ...,
        gt=0,
        title="Expiration time",
        description="Token validity duration in seconds",
        examples=[3600],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "user": {
                    "name": "john_doe",
                    "role": "user",
                    "is_active": True,
                },
                "expires_in": 3600,
            }
        }
    )
