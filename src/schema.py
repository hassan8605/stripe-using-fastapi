"""
src/schema.py
─────────────
Shared base schemas used across modules.
Each feature module has its own schema.py for feature-specific models.
"""

from pydantic import BaseModel
from typing import Optional, Any


class BaseResponse(BaseModel):
    """Standard wrapper — optional, use when you want a consistent envelope."""
    success: bool = True
    message: str = "OK"
    data: Optional[Any] = None


class MessageResponse(BaseModel):
    message: str


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
