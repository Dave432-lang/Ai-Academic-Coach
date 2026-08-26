class UniversityModel {
  final String id;
  final String name;
  final String country;
  final String? website;
  final String? timezone;

  UniversityModel({
    required this.id,
    required this.name,
    required this.country,
    this.website,
    this.timezone,
  });

  factory UniversityModel.fromJson(Map<String, dynamic> json) {
    return UniversityModel(
      id: json['id'] as String,
      name: json['name'] as String,
      country: json['country'] as String,
      website: json['website'] as String?,
      timezone: json['timezone'] as String?,
    );
  }
}

class StudentProfileModel {
  final String id;
  final String userId;
  final String fullName;
  final String? country;
  final String timezone;
  final String? universityId;
  final String? universityName;
  final String? program;
  final String? level;
  final String? academicYear;
  final String? semester;
  final bool onboardingCompleted;
  final DateTime? onboardingCompletedAt;

  StudentProfileModel({
    required this.id,
    required this.userId,
    required this.fullName,
    this.country,
    required this.timezone,
    this.universityId,
    this.universityName,
    this.program,
    this.level,
    this.academicYear,
    this.semester,
    required this.onboardingCompleted,
    this.onboardingCompletedAt,
  });

  factory StudentProfileModel.fromJson(Map<String, dynamic> json) {
    return StudentProfileModel(
      id: json['id'] as String,
      userId: json['user_id'] as String,
      fullName: json['full_name'] as String,
      country: json['country'] as String?,
      timezone: json['timezone'] as String? ?? 'UTC',
      universityId: json['university_id'] as String?,
      universityName: json['university_name'] as String?,
      program: json['program'] as String?,
      level: json['level'] as String?,
      academicYear: json['academic_year'] as String?,
      semester: json['semester'] as String?,
      onboardingCompleted: json['onboarding_completed'] as bool? ?? false,
      onboardingCompletedAt: json['onboarding_completed_at'] != null
          ? DateTime.parse(json['onboarding_completed_at'] as String)
          : null,
    );
  }
}

class CourseEnrollmentModel {
  final String id;
  final String courseId;
  final String courseCode;
  final String courseName;
  final String academicYear;
  final String semester;
  final String status;

  CourseEnrollmentModel({
    required this.id,
    required this.courseId,
    required this.courseCode,
    required this.courseName,
    required this.academicYear,
    required this.semester,
    required this.status,
  });

  factory CourseEnrollmentModel.fromJson(Map<String, dynamic> json) {
    return CourseEnrollmentModel(
      id: json['id'] as String,
      courseId: json['course_id'] as String,
      courseCode: json['course_code'] as String,
      courseName: json['course_name'] as String,
      academicYear: json['academic_year'] as String,
      semester: json['semester'] as String,
      status: json['status'] as String,
    );
  }
}

class OnboardingStatusModel {
  final bool onboardingCompleted;
  final bool hasProfile;
  final bool hasUniversity;
  final bool hasAcademicInfo;
  final int activeCourseCount;
  final List<String> missingRequirements;

  OnboardingStatusModel({
    required this.onboardingCompleted,
    required this.hasProfile,
    required this.hasUniversity,
    required this.hasAcademicInfo,
    required this.activeCourseCount,
    required this.missingRequirements,
  });

  factory OnboardingStatusModel.fromJson(Map<String, dynamic> json) {
    return OnboardingStatusModel(
      onboardingCompleted: json['onboarding_completed'] as bool? ?? false,
      hasProfile: json['has_profile'] as bool? ?? false,
      hasUniversity: json['has_university'] as bool? ?? false,
      hasAcademicInfo: json['has_academic_info'] as bool? ?? false,
      activeCourseCount: json['active_course_count'] as int? ?? 0,
      missingRequirements: (json['missing_requirements'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          [],
    );
  }
}
