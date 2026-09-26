from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, File, Form, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database.connection import get_db
from app.database.models import User
from app.schemas.material import CourseMaterialResponse, MaterialDeleteResponse, MaterialUploadResponse
from app.services.material_service import (
    delete_course_material,
    download_course_material,
    get_course_material_metadata,
    list_course_materials,
    upload_course_material,
)

router = APIRouter(prefix="/materials", tags=["Course Materials"])


@router.post("", response_model=CourseMaterialResponse, status_code=status.HTTP_201_CREATED)
def upload_material(
    course_id: uuid.UUID = Form(...),
    title: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload a new course material (PDF, DOCX, PPTX, DOC, PPT).
    Validates ownership of course_id, file size, and magic bytes signature.
    """
    return upload_course_material(
        db=db,
        user_id=current_user.id,
        course_id=course_id,
        file=file,
        custom_title=title,
    )


@router.get("", response_model=List[CourseMaterialResponse])
def get_materials(
    course_id: Optional[uuid.UUID] = Query(None, description="Filter materials by enrolled course_id"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List uploaded course materials for the authenticated student.
    Optionally filterable by course_id.
    """
    return list_course_materials(
        db=db,
        user_id=current_user.id,
        course_id=course_id,
    )


@router.get("/{material_id}", response_model=CourseMaterialResponse)
def get_material_metadata(
    material_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve metadata for a single uploaded course material.
    """
    return get_course_material_metadata(
        db=db,
        user_id=current_user.id,
        material_id=material_id,
    )


@router.get("/{material_id}/download")
def download_material(
    material_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Stream/download a previously uploaded course material file.
    Validates student ownership before serving content.
    """
    return download_course_material(
        db=db,
        user_id=current_user.id,
        material_id=material_id,
    )


@router.delete("/{material_id}", response_model=MaterialDeleteResponse)
def delete_material(
    material_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete a course material database record and its file on disk.
    Handles missing files on disk gracefully.
    """
    deleted_id = delete_course_material(
        db=db,
        user_id=current_user.id,
        material_id=material_id,
    )
    return MaterialDeleteResponse(
        message="Course material deleted successfully",
        material_id=deleted_id,
    )
