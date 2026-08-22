import enum


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    PENDING = "pending"
    DELETED = "deleted"


class EnrollmentStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DROPPED = "dropped"
    WITHDRAWN = "withdrawn"


class EventType(str, enum.Enum):
    ASSIGNMENT = "assignment"
    QUIZ = "quiz"
    EXAM = "exam"
    PROJECT = "project"
    PRESENTATION = "presentation"
    OTHER = "other"


class PriorityLevel(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AcademicStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    MISSED = "missed"


class GoalStatus(str, enum.Enum):
    ACTIVE = "active"
    ACHIEVED = "achieved"
    PAUSED = "paused"
    CANCELLED = "cancelled"


class MaterialProcessingStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class MessageRole(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class MemoryType(str, enum.Enum):
    PREFERENCE = "preference"
    GOAL = "goal"
    ACADEMIC_CONTEXT = "academic_context"
    LEARNING_PATTERN = "learning_pattern"


class AgentType(str, enum.Enum):
    COORDINATOR = "coordinator"
    PLANNER = "planner"
    STUDY = "study"
    PROGRESS = "progress"


class ActionStatus(str, enum.Enum):
    PENDING = "pending"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PermissionMode(str, enum.Enum):
    ALLOW = "allow"
    REQUIRE_APPROVAL = "require_approval"
    REQUIRE_CONFIRMATION = "require_confirmation"
    DENY = "deny"


class NotificationStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    SENT = "sent"
    READ = "read"
    DISMISSED = "dismissed"
    FAILED = "failed"
    CANCELLED = "cancelled"
