from datetime import datetime
from typing import List

from pydantic import BaseModel, Field

from api.models.prediction import PredictionLabel


class PredictionCreate(BaseModel):
    """Payload d'entrée pour une prédiction"""

    title: str = Field(..., min_length=1, max_length=300)


class PredictionListCreate(BaseModel):
    """Payload pour prédiction en lot"""

    titles: List[str] = Field(..., min_length=1, max_length=50)


class PredictionResponse(BaseModel):
    """Réponse d'une prédiction"""

    id: int
    user_id: int
    title: str
    predicted_label: PredictionLabel
    confidence: float
    created_at: datetime

    class Config:
        from_attributes = True


class PredictionListResponse(BaseModel):
    """Liste de prédictions"""

    predictions: list[PredictionResponse]
