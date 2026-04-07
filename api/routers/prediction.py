from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.core.database import get_db
from api.dependencies.auth import require_roles
from api.dependencies.ml_model import get_model
from api.models.user import User, UserRole
from api.schemas.prediction import (
    PredictionCreate,
    PredictionListCreate,
    PredictionListResponse,
    PredictionResponse,
)
from api.schemas.utils import APIResponse
from api.services.prediction import (
    create_prediction,
    get_prediction_by_id,
    get_predictions_by_user_id,
)
from api.utils.logger import get_logger
from api.utils.ml_model import MLModel

logger = get_logger()

router = APIRouter(prefix="/predictions", tags=["Predictions"])


def validate_title(title: str) -> None:
    if title.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Title must not be empty or whitespace only",
        )

    if len(title) > 300:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title must not exceed 300 characters",
        )


def validate_batch_titles(titles: list[str]) -> None:
    if len(titles) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Titles list must not be empty",
        )

    if len(titles) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 50 titles allowed per batch",
        )

    for title in titles:
        validate_title(title)


@router.post(
    "",
    response_model=APIResponse[PredictionResponse],
    status_code=status.HTTP_201_CREATED,
)
def predict(
    input_data: PredictionCreate,
    db: Session = Depends(get_db),
    ml_model: MLModel = Depends(get_model),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.USER)),
) -> APIResponse[PredictionResponse]:
    logger.info(
        f"Prediction request : user_id={current_user.id}",
    )

    validate_title(input_data.title)

    try:
        predicted_label, confidence = ml_model.predict([input_data.title])

        prediction = create_prediction(
            db=db,
            user_id=current_user.id,
            title=input_data.title,
            predicted_label=predicted_label[0],
            confidence=confidence[0],
        )

        logger.info(
            f"Prediction created : user_id={current_user.id}, prediction_id={prediction.id}, label={predicted_label[0]}"
        )

        return APIResponse(
            status=True,
            data=prediction,
            message="Prediction successfully created",
            timestamp=datetime.now(timezone.utc),
        )

    except Exception as e:
        logger.exception(
            f"Prediction failed : user_id={current_user.id}",
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed : {e}",
        )


@router.post(
    "/batch",
    response_model=APIResponse[PredictionListResponse],
    status_code=status.HTTP_200_OK,
)
def predict_batch(
    input_data: PredictionListCreate,
    db: Session = Depends(get_db),
    ml_model: MLModel = Depends(get_model),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.USER)),
) -> APIResponse[PredictionListResponse]:
    logger.info(
        f"Batch prediction request: user_id={current_user.id}, batch_size={len(input_data.titles)}"
    )

    validate_batch_titles(input_data.titles)

    try:
        predicted_labels, confidences = ml_model.predict(input_data.titles)

        predictions = []

        for title, label, conf in zip(input_data.titles, predicted_labels, confidences):
            prediction = create_prediction(
                db=db,
                user_id=current_user.id,
                title=title,
                predicted_label=label,
                confidence=conf,
            )

            predictions.append(prediction)

        logger.info(
            f"Batch prediction completed : user_id={current_user.id}, count={len(predictions)}"
        )

        return APIResponse(
            status=True,
            data=PredictionListResponse(predictions=predictions),
            message="Batch prediction completed successfully",
            timestamp=datetime.now(timezone.utc),
        )

    except Exception as e:
        logger.exception(f"Batch prediction failed : user_id={current_user.id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed : {e}",
        )


@router.get(
    "/me",
    response_model=APIResponse[PredictionListResponse],
)
def get_my_predictions(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.USER)),
) -> APIResponse[PredictionListResponse]:
    logger.info(
        f"Fetch user predictions : user_id={current_user.id}",
    )

    predictions = get_predictions_by_user_id(db, current_user.id)

    logger.info(
        f"User predictions retrieved : user_id={current_user.id}, count={len(predictions)}"
    )

    return APIResponse(
        status=True,
        data=PredictionListResponse(predictions=predictions),
        message="User predictions retrieved successfully",
        timestamp=datetime.now(timezone.utc),
    )


@router.get(
    "/{prediction_id}",
    response_model=APIResponse[PredictionResponse],
)
def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.USER)),
) -> APIResponse[PredictionResponse]:
    logger.info(
        f"Fetch prediction : user_id={current_user.id}, prediction_id={prediction_id}"
    )

    prediction = get_prediction_by_id(db, prediction_id)

    if not prediction:
        logger.warning(f"Prediction not found : prediction_id={prediction_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prediction not found",
        )

    if prediction.user_id != current_user.id and current_user.role != UserRole.ADMIN:
        logger.warning(
            f"Unauthorized prediction access : user_id={current_user.id}, prediction_id={prediction_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to access this prediction",
        )

    return APIResponse(
        status=True,
        data=prediction,
        message="Prediction retrieved successfully",
        timestamp=datetime.now(timezone.utc),
    )
