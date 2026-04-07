from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    status: bool
    data: T
    message: str
    timestamp: datetime


class MessageResponse(BaseModel):
    message: str
