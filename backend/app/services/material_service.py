import os
import uuid
import re
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import get_logger
from app.database.models import CourseMaterial, Course, MaterialProcessingStatus
from app.schemas.material import CourseMaterialResponse
from app.services.course_service import get_student_profile_by_user_id, verify_course_enrollment

logger = get_logger("material_service")

ALLOWED_EXTENSIONS = {".pdf", ".pptx", ".docx", ".doc", ".ppt"}
ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    "application/msword",
    "application/vnd.ms-powerpoint",
    "application/octet-stream",
}

# Magic byte signatures
PDF_MAGIC = b"%PDF-"
ZIP_MAGIC = b"PK\x03\x04"  # Used by DOCX, PPTX
OLE_MAGIC = b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"  # Used by legacy DOC, PPT


def sanitize_filename(filename: str) -> str:
    """
    Sanitize client-provided filename to prevent path traversal and shell injection.
    Strips directory components and dangerous characters.
    """
    if not filename:
        return "unnamed_material"
    # Take basename to strip directory paths
    clean_name = os.path.basename(filename)
    # Remove null bytes and path traversal sequences
    clean_name = clean_name.replace("\x00", "").replace("..", "")
    # Sanitize characters: keep alphanumeric, dots, underscores, dashes, spaces
    clean_name = re.sub(r"[^\w\s\.-]", "_", clean_name).strip()
    return clean_name if clean_name else "unnamed_material"


def validate_file_content(file_bytes: bytes, filename: str, content_type: Optional[str]) -> str:
    """
    Validate file extension, MIME type, and magic byte signatures.
    Returns normalized file_type string or raises 415 Unsupported Media Type.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File extension '{ext}' is not allowed. Supported formats: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Magic byte verification
    header = file_bytes[:8]
    valid_signature = False

    if ext == ".pdf":
        if header.startswith(PDF_MAGIC):
            valid_signature = True
            norm_type = "application/pdf"
    elif ext in (".docx", ".pptx"):
        if header.startswith(ZIP_MAGIC):
            valid_signature = True
            norm_type = (
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                if ext == ".docx"
                else "application/vnd.openxmlformats-officedocument.presentationml.presentation"
            )
    elif ext in (".doc", ".ppt"):
        if header.startswith(OLE_MAGIC):
            valid_signature = True
            norm_type = "application/msword" if ext == ".doc" else "application/vnd.ms-powerpoint"

    if not valid_signature:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"File header magic bytes do not match expected signature for extension '{ext}'",
        )

    return norm_type


def get_absolute_storage_path(storage_key: str) -> str:
    """
    Resolve absolute path on disk for a given storage_key, enforcing root directory containment.
    """
    base_dir = os.path.abspath(settings.STORAGE_PATH)
    abs_path = os.path.abspath(os.path.join(base_dir, storage_key))
    if not abs_path.startswith(base_dir):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Illegal storage key path traversal attempt detected",
        )
    return abs_path


def upload_course_material(
    db: Session,
    user_id: uuid.UUID,
    course_id: uuid.UUID,
    file: UploadFile,
    custom_title: Optional[str] = None,
) -> CourseMaterialResponse:
    """
    Upload and store course material for an enrolled student.
    Validates ownership, file size, type/magic bytes, and stores file outside git tree.
    """
    profile = get_student_profile_by_user_id(db, user_id)
    student_id = profile.id

    # Verify student is enrolled in the specified course
    verify_course_enrollment(db, student_id, course_id)

    raw_filename = file.filename or "unnamed_material"
    sanitized_name = sanitize_filename(raw_filename)
    if custom_title and custom_title.strip():
        display_name = custom_title.strip()
        # Preserve original extension on custom title if missing
        ext = os.path.splitext(sanitized_name)[1]
        if not display_name.lower().endswith(ext.lower()):
            display_name += ext
    else:
        display_name = sanitized_name

    # Read content to check size and magic bytes
    try:
        file_bytes = file.file.read()
    except Exception as e:
        logger.error(f"Failed to read upload file stream: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to read uploaded file content",
        )

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    actual_size = len(file_bytes)
    if actual_size > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size ({actual_size / (1024*1024):.2f} MB) exceeds maximum limit of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )
    if actual_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)",
        )

    # Validate file type and magic bytes
    file_type = validate_file_content(file_bytes, sanitized_name, file.content_type)

    # Generate unique storage key (relative path)
    ext = os.path.splitext(sanitized_name)[1].lower()
    unique_filename = f"{uuid.uuid4()}{ext}"
    storage_key = os.path.join(str(student_id), str(course_id), unique_filename).replace("\\", "/")

    abs_path = get_absolute_storage_path(storage_key)

    # Ensure parent directory exists
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)

    # Write file to disk first
    try:
        with open(abs_path, "wb") as f:
            f.write(file_bytes)
    except Exception as e:
        logger.error(f"Error writing file to disk ({abs_path}): {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store file on disk",
        )

    # Database insert with cleanup safety
    try:
        material = CourseMaterial(
            student_id=student_id,
            course_id=course_id,
            file_name=display_name,
            file_type=file_type,
            storage_key=storage_key,
            file_size=actual_size,
            processing_status=MaterialProcessingStatus.PENDING,
        )
        db.add(material)
        db.commit()
        db.refresh(material)
    except Exception as e:
        db.rollback()
        # Clean up written file from disk on DB failure
        if os.path.exists(abs_path):
            try:
                os.remove(abs_path)
            except Exception:
                pass
        logger.error(f"Database error saving CourseMaterial record: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create material record in database",
        )

    course = db.query(Course).filter(Course.id == course_id).first()
    return CourseMaterialResponse(
        id=material.id,
        student_id=material.student_id,
        course_id=material.course_id,
        file_name=material.file_name,
        file_type=material.file_type,
        storage_key=material.storage_key,
        file_size=material.file_size,
        processing_status=material.processing_status,
        created_at=material.created_at,
        updated_at=material.updated_at,
        course_code=course.course_code if course else None,
        course_name=course.course_name if course else None,
    )


def list_course_materials(
    db: Session,
    user_id: uuid.UUID,
    course_id: Optional[uuid.UUID] = None,
) -> List[CourseMaterialResponse]:
    """
    List all materials uploaded by the authenticated student, optionally filtered by course_id.
    """
    profile = get_student_profile_by_user_id(db, user_id)
    query = (
        db.query(CourseMaterial, Course)
        .join(Course, CourseMaterial.course_id == Course.id)
        .filter(CourseMaterial.student_id == profile.id)
    )
    if course_id:
        # Verify enrollment for course_id filter if provided
        verify_course_enrollment(db, profile.id, course_id)
        query = query.filter(CourseMaterial.course_id == course_id)

    results = query.order_by(CourseMaterial.created_at.desc()).all()
    out = []
    for mat, crs in results:
        out.append(
            CourseMaterialResponse(
                id=mat.id,
                student_id=mat.student_id,
                course_id=mat.course_id,
                file_name=mat.file_name,
                file_type=mat.file_type,
                storage_key=mat.storage_key,
                file_size=mat.file_size,
                processing_status=mat.processing_status,
                created_at=mat.created_at,
                updated_at=mat.updated_at,
                course_code=crs.course_code,
                course_name=crs.course_name,
            )
        )
    return out


def get_course_material_metadata(
    db: Session,
    user_id: uuid.UUID,
    material_id: uuid.UUID,
) -> CourseMaterialResponse:
    """
    Retrieve metadata for a single material owned by the authenticated student.
    """
    profile = get_student_profile_by_user_id(db, user_id)
    res = (
        db.query(CourseMaterial, Course)
        .join(Course, CourseMaterial.course_id == Course.id)
        .filter(
            CourseMaterial.id == material_id,
            CourseMaterial.student_id == profile.id,
        )
        .first()
    )
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found or access denied",
        )
    mat, crs = res
    return CourseMaterialResponse(
        id=mat.id,
        student_id=mat.student_id,
        course_id=mat.course_id,
        file_name=mat.file_name,
        file_type=mat.file_type,
        storage_key=mat.storage_key,
        file_size=mat.file_size,
        processing_status=mat.processing_status,
        created_at=mat.created_at,
        updated_at=mat.updated_at,
        course_code=crs.course_code,
        course_name=crs.course_name,
    )


def download_course_material(
    db: Session,
    user_id: uuid.UUID,
    material_id: uuid.UUID,
) -> FileResponse:
    """
    Stream/serve the physical file for a material owned by the student.
    Sets appropriate Content-Type and Content-Disposition headers.
    """
    profile = get_student_profile_by_user_id(db, user_id)
    mat = (
        db.query(CourseMaterial)
        .filter(
            CourseMaterial.id == material_id,
            CourseMaterial.student_id == profile.id,
        )
        .first()
    )
    if not mat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found or access denied",
        )

    abs_path = get_absolute_storage_path(mat.storage_key)
    if not os.path.exists(abs_path):
        logger.warning(f"File missing on disk for material {material_id} at {abs_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material file does not exist on disk",
        )

    return FileResponse(
        path=abs_path,
        media_type=mat.file_type,
        filename=mat.file_name,
        headers={"Content-Disposition": f'inline; filename="{mat.file_name}"'},
    )


def delete_course_material(
    db: Session,
    user_id: uuid.UUID,
    material_id: uuid.UUID,
) -> uuid.UUID:
    """
    Delete a course material database record AND its underlying file on disk.
    Gracefully handles cases where file is missing from disk.
    """
    profile = get_student_profile_by_user_id(db, user_id)
    mat = (
        db.query(CourseMaterial)
        .filter(
            CourseMaterial.id == material_id,
            CourseMaterial.student_id == profile.id,
        )
        .first()
    )
    if not mat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found or access denied",
        )

    # Remove physical file if present
    abs_path = get_absolute_storage_path(mat.storage_key)
    if os.path.exists(abs_path):
        try:
            os.remove(abs_path)
            # Try removing empty parent directories if clean
            parent_dir = os.path.dirname(abs_path)
            if not os.listdir(parent_dir):
                os.rmdir(parent_dir)
        except Exception as e:
            logger.warning(f"Failed to remove file/dir from disk ({abs_path}): {str(e)}")
    else:
        logger.warning(f"File already missing from disk during deletion: {abs_path}")

    # Remove DB row
    db.delete(mat)
    db.commit()
    return material_id
