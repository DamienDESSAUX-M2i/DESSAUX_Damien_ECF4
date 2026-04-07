from datetime import datetime, timezone
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.core.database import Base
from api.models.user import User


class PredictionLabel(StrEnum):
    FAKE = "FAKE"
    REAL = "REAL"


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user: Mapped[User] = relationship(foreign_keys=[user_id])
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    predicted_label: Mapped[PredictionLabel] = mapped_column(
        Enum(PredictionLabel), nullable=False, index=True
    )
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.now(timezone.utc), nullable=False
    )
