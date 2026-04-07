from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Standard API response wrapper."""

    status: bool = Field(
        ...,
        title="Status",
        description="Indicates whether the request was successful",
        examples=[True],
    )

    data: T = Field(
        ...,
        title="Response data",
        description="Payload returned by the API (can vary depending on the endpoint)",
    )

    message: str = Field(
        ...,
        title="Message",
        description="Human-readable message describing the result",
        examples=["Request processed successfully"],
    )

    timestamp: datetime = Field(
        ...,
        title="Timestamp",
        description="UTC timestamp when the response was generated",
        examples=["2026-04-07T12:00:00Z"],
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": True,
                "data": {},
                "message": "Request processed successfully",
                "timestamp": "2026-04-07T12:00:00Z",
            }
        }
    )


class MessageResponse(BaseModel):
    """Simple message response schema."""

    message: str = Field(
        ...,
        title="Message",
        description="Human-readable message",
        examples=["Operation completed successfully"],
    )

    model_config = ConfigDict(
        json_schema_extra={"example": {"message": "Operation completed successfully"}}
    )
