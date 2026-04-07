from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from api.dependencies.ml_model import get_model
from api.schemas.utils import APIResponse, MessageResponse
from api.utils.ml_model import MLModel

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/", response_model=APIResponse[MessageResponse])
async def health_check(
    ml_model: MLModel = Depends(get_model),
) -> APIResponse[MessageResponse]:
    """Check health of the API"""
    if ml_model is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded",
        )
    return APIResponse(
        status=True,
        data=MessageResponse(message="Model loaded"),
        message="Healthy",
        timestamp=datetime.now(timezone.utc),
    )
