from datetime import datetime
from typing import Annotated, List

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

from api.models.prediction import PredictionLabel

TitleStr = Annotated[str, StringConstraints(min_length=1, max_length=300)]


class PredictionCreate(BaseModel):
    """Input payload for a single prediction request."""

    title: TitleStr = Field(
        ...,
        title="Article title",
        description="Title of the article to classify as FAKE or REAL",
        examples=["Breaking news: major discovery in AI research"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"title": "Breaking news: major discovery in AI research"}
        }
    )


class PredictionListCreate(BaseModel):
    """Input payload for batch prediction requests."""

    titles: List[TitleStr] = Field(
        ...,
        min_length=1,
        max_length=50,
        title="List of article titles",
        description="List of article titles to classify in batch mode",
        examples=[
            [
                "Breaking news: major discovery in AI research",
                "Celebrity announces new album release",
            ]
        ],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "titles": [
                    "Breaking news: major discovery in AI research",
                    "Celebrity announces new album release",
                ]
            }
        }
    )


class PredictionResponse(BaseModel):
    """Response for a single prediction."""

    id: int = Field(
        ...,
        title="Prediction ID",
        description="Unique identifier of the prediction",
        examples=[1],
    )

    user_id: int = Field(
        ...,
        title="User ID",
        description="Identifier of the user who made the prediction",
        examples=[42],
    )

    title: str = Field(
        ...,
        title="Article title",
        description="Original title submitted for prediction",
        examples=["Breaking news: major discovery in AI research"],
    )

    predicted_label: PredictionLabel = Field(
        ...,
        title="Predicted label",
        description="Classification result of the model (FAKE or REAL)",
        examples=["FAKE"],
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        title="Confidence score",
        description="Model confidence score between 0 and 1",
        examples=[0.93],
    )

    created_at: datetime = Field(
        ...,
        title="Creation timestamp",
        description="Timestamp when the prediction was created",
        examples=["2026-04-07T12:00:00Z"],
    )

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "user_id": 42,
                "title": "Breaking news: major discovery in AI research",
                "predicted_label": "FAKE",
                "confidence": 0.93,
                "created_at": "2026-04-07T12:00:00Z",
            }
        },
    )


class PredictionListResponse(BaseModel):
    """Response containing a list of predictions."""

    predictions: List[PredictionResponse] = Field(
        ...,
        title="Predictions",
        description="List of prediction results",
        examples=[],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "predictions": [
                    {
                        "id": 1,
                        "user_id": 42,
                        "title": "Breaking news: major discovery in AI research",
                        "predicted_label": "FAKE",
                        "confidence": 0.93,
                        "created_at": "2026-04-07T12:00:00Z",
                    },
                    {
                        "id": 2,
                        "user_id": 42,
                        "title": "Government releases official economic report",
                        "predicted_label": "REAL",
                        "confidence": 0.97,
                        "created_at": "2026-04-07T12:05:00Z",
                    },
                ]
            }
        },
    )
