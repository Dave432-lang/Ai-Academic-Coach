from datetime import datetime
from typing import Optional
import uuid
from pydantic import BaseModel, ConfigDict
from app.database.models.enums import MaterialProcessingStatus


class CourseMaterialResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    course_id: uuid.UUID
    file_name: str
    file_type: str
    storage_key: str
    file_size: Optional[int] = None
    processing_status: MaterialProcessingStatus
    created_at: datetime
    updated_at: datetime
    course_code: Optional[str] = None
    course_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MaterialUploadResponse(BaseModel):
    message: str
    material: CourseMaterialResponse


class MaterialDeleteResponse(BaseModel):
    message: str
    material_id: uuid.UUID
