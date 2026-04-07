from fastapi import HTTPException, Request

from api.utils.ml_model import MLModel


def get_model(request: Request) -> MLModel:
    model = request.app.state.ml_model

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model not loaded",
        )

    return model
