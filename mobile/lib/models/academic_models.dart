class CourseDetailModel {
  final String id;
  final String courseCode;
  final String courseName;
  final String? description;
  final int? creditHours;

  CourseDetailModel({
    required this.id,
    required this.courseCode,
    required this.courseName,
    this.description,
    this.creditHours,
  });

  factory CourseDetailModel.fromJson(Map<String, dynamic> json) {
    return CourseDetailModel(
      id: json['id'] as String,
      courseCode: json['course_code'] as String,
      courseName: json['course_name'] as String,
      description: json['description'] as String?,
      creditHours: json['credit_hours'] as int?,
    );
  }
}

class AcademicCourseEnrollmentModel {
  final String id;
  final String courseId;
  final String status;
  final String? academicYear;
  final String? semester;
  final CourseDetailModel course;

  AcademicCourseEnrollmentModel({
    required this.id,
    required this.courseId,
    required this.status,
    this.academicYear,
    this.semester,
    required this.course,
  });

  factory AcademicCourseEnrollmentModel.fromJson(Map<String, dynamic> json) {
    return AcademicCourseEnrollmentModel(
      id: json['id'] as String,
      courseId: json['course_id'] as String,
      status: json['status'] as String,
      academicYear: json['academic_year'] as String?,
      semester: json['semester'] as String?,
      course: CourseDetailModel.fromJson(json['course'] as Map<String, dynamic>),
    );
  }
}

class AcademicEventModel {
  final String id;
  final String studentId;
  final String courseId;
  final String eventType;
  final String title;
  final String? description;
  final DateTime dueAt;
  final String priority;
  final String status;
  final DateTime createdAt;

  AcademicEventModel({
    required this.id,
    required this.studentId,
    required this.courseId,
    required this.eventType,
    required this.title,
    this.description,
    required this.dueAt,
    required this.priority,
    required this.status,
    required this.createdAt,
  });

  factory AcademicEventModel.fromJson(Map<String, dynamic> json) {
    return AcademicEventModel(
      id: json['id'] as String,
      studentId: json['student_id'] as String,
      courseId: json['course_id'] as String,
      eventType: json['event_type'] as String,
      title: json['title'] as String,
      description: json['description'] as String?,
      dueAt: DateTime.parse(json['due_at'] as String),
      priority: json['priority'] as String,
      status: json['status'] as String,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class TaskModel {
  final String id;
  final String studentId;
  final String? courseId;
  final String? academicEventId;
  final String title;
  final String? description;
  final String priority;
  final String status;
  final int? estimatedMinutes;
  final DateTime? dueDate;

  TaskModel({
    required this.id,
    required this.studentId,
    this.courseId,
    this.academicEventId,
    required this.title,
    this.description,
    required this.priority,
    required this.status,
    this.estimatedMinutes,
    this.dueDate,
  });

  factory TaskModel.fromJson(Map<String, dynamic> json) {
    return TaskModel(
      id: json['id'] as String,
      studentId: json['student_id'] as String,
      courseId: json['course_id'] as String?,
      academicEventId: json['academic_event_id'] as String?,
      title: json['title'] as String,
      description: json['description'] as String?,
      priority: json['priority'] as String,
      status: json['status'] as String,
      estimatedMinutes: json['estimated_minutes'] as int?,
      dueDate: json['due_date'] != null ? DateTime.parse(json['due_date'] as String) : null,
    );
  }
}

class StudySessionModel {
  final String id;
  final String studentId;
  final String? courseId;
  final String? taskId;
  final DateTime scheduledStart;
  final DateTime scheduledEnd;
  final String? topic;
  final String? notes;
  final String status;
  final int completionPercentage;

  StudySessionModel({
    required this.id,
    required this.studentId,
    this.courseId,
    this.taskId,
    required this.scheduledStart,
    required this.scheduledEnd,
    this.topic,
    this.notes,
    required this.status,
    required this.completionPercentage,
  });

  factory StudySessionModel.fromJson(Map<String, dynamic> json) {
    return StudySessionModel(
      id: json['id'] as String,
      studentId: json['student_id'] as String,
      courseId: json['course_id'] as String?,
      taskId: json['task_id'] as String?,
      scheduledStart: DateTime.parse(json['scheduled_start'] as String),
      scheduledEnd: DateTime.parse(json['scheduled_end'] as String),
      topic: json['topic'] as String?,
      notes: json['notes'] as String?,
      status: json['status'] as String,
      completionPercentage: (json['completion_percentage'] as num).toInt(),
    );
  }
}

class GoalModel {
  final String id;
  final String studentId;
  final String? courseId;
  final String title;
  final String? description;
  final double targetValue;
  final double currentValue;
  final DateTime? targetDate;
  final String status;

  GoalModel({
    required this.id,
    required this.studentId,
    this.courseId,
    required this.title,
    this.description,
    required this.targetValue,
    required this.currentValue,
    this.targetDate,
    required this.status,
  });

  factory GoalModel.fromJson(Map<String, dynamic> json) {
    return GoalModel(
      id: json['id'] as String,
      studentId: json['student_id'] as String,
      courseId: json['course_id'] as String?,
      title: json['title'] as String,
      description: json['description'] as String?,
      targetValue: (json['target_value'] as num).toDouble(),
      currentValue: (json['current_value'] as num).toDouble(),
      targetDate: json['target_date'] != null ? DateTime.parse(json['target_date'] as String) : null,
      status: json['status'] as String,
    );
  }
}

class GradeModel {
  final String id;
  final String studentId;
  final String courseId;
  final String assessmentName;
  final String? assessmentType;
  final double score;
  final double maxScore;
  final double? percentage;

  GradeModel({
    required this.id,
    required this.studentId,
    required this.courseId,
    required this.assessmentName,
    this.assessmentType,
    required this.score,
    required this.maxScore,
    this.percentage,
  });

  factory GradeModel.fromJson(Map<String, dynamic> json) {
    return GradeModel(
      id: json['id'] as String,
      studentId: json['student_id'] as String,
      courseId: json['course_id'] as String,
      assessmentName: json['assessment_name'] as String,
      assessmentType: json['assessment_type'] as String?,
      score: json['score'] is num
          ? (json['score'] as num).toDouble()
          : double.parse(json['score'].toString()),
      maxScore: json['max_score'] is num
          ? (json['max_score'] as num).toDouble()
          : double.parse(json['max_score'].toString()),
      percentage: json['percentage'] != null
          ? (json['percentage'] is num
              ? (json['percentage'] as num).toDouble()
              : double.parse(json['percentage'].toString()))
          : null,
    );
  }

}

class DashboardSummaryModel {
  final String studentName;
  final bool onboardingCompleted;
  final int enrolledCoursesCount;
  final int upcomingEventsCount;
  final int activeTasksCount;
  final int studySessionsThisWeekCount;
  final List<GradeModel> recentGrades;

  DashboardSummaryModel({
    required this.studentName,
    required this.onboardingCompleted,
    required this.enrolledCoursesCount,
    required this.upcomingEventsCount,
    required this.activeTasksCount,
    required this.studySessionsThisWeekCount,
    required this.recentGrades,
  });

  factory DashboardSummaryModel.fromJson(Map<String, dynamic> json) {
    return DashboardSummaryModel(
      studentName: json['student_name'] as String,
      onboardingCompleted: json['onboarding_completed'] as bool,
      enrolledCoursesCount: json['enrolled_courses_count'] as int,
      upcomingEventsCount: json['upcoming_events_count'] as int,
      activeTasksCount: json['active_tasks_count'] as int,
      studySessionsThisWeekCount: json['study_sessions_this_week_count'] as int,
      recentGrades: (json['recent_grades'] as List<dynamic>)
          .map((item) => GradeModel.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}
