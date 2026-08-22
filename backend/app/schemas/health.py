from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """
    Schema for health check endpoint response.
    """
    status: str = Field(..., json_schema_extra={"example": "ok"})
    app: Optional[str] = Field(None, json_schema_extra={"example": "AI Academic Coach API"})
    version: Optional[str] = Field(None, json_schema_extra={"example": "0.1.0"})
    environment: Optional[str] = Field(None, json_schema_extra={"example": "development"})
    database: Optional[Dict[str, Any]] = Field(None)
