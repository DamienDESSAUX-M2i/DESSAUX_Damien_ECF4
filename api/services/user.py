from typing import Optional

from sqlalchemy.orm import Session

from api.core.security import hash_password
from api.models.user import User, UserRole


def get_user_by_name(db: Session, name: str) -> Optional[User]:
    return db.query(User).filter(User.name == name).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_all_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id.asc()).all()


def create_user(
    db: Session,
    name: str,
    password: str,
    role: UserRole | str = UserRole.USER.value,
    is_active: bool = True,
) -> User:
    password_hash = hash_password(password)

    user = User(
        name=name,
        password_hash=password_hash,
        role=role.value if isinstance(role, UserRole) else role,
        is_active=is_active,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def delete_user_by_id(db: Session, user_id: int) -> Optional[User]:
    user = get_user_by_id(db, user_id)
    if not user:
        return None

    db.delete(user)
    db.commit()
    return user
