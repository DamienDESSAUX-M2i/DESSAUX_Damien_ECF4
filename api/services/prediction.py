from typing import List, Optional

from sqlalchemy.orm import Session

from api.models.prediction import Prediction, PredictionLabel


def get_prediction_by_id(db: Session, prediction_id: int) -> Optional[Prediction]:
    return db.query(Prediction).filter(Prediction.id == prediction_id).first()


def get_predictions_by_user_id(db: Session, user_id: int) -> List[Prediction]:
    return (
        db.query(Prediction)
        .filter(Prediction.user_id == user_id)
        .order_by(Prediction.created_at.desc())
        .all()
    )


def get_all_predictions(db: Session) -> List[Prediction]:
    return db.query(Prediction).order_by(Prediction.created_at.desc()).all()


def create_prediction(
    db: Session,
    user_id: int,
    title: str,
    predicted_label: PredictionLabel,
    confidence: float,
) -> Prediction:
    prediction = Prediction(
        user_id=user_id,
        title=title,
        predicted_label=predicted_label.value,
        confidence=confidence,
    )

    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction
