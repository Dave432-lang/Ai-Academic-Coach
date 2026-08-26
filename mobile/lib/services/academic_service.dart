import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/config/api_config.dart';
import '../models/academic_models.dart';
import 'auth_service.dart';

class AcademicService {
  final http.Client client;
  final AuthService authService;

  AcademicService({
    required this.authService,
    http.Client? client,
  }) : client = client ?? http.Client();

  /// Dashboard Summary
  Future<DashboardSummaryModel> fetchDashboardSummary() async {
    final uri = Uri.parse(ApiConfig.dashboardSummaryEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);

    if (response.statusCode == 200) {
      return DashboardSummaryModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load dashboard summary: ${response.body}');
    }
  }

  /// Courses
  Future<List<AcademicCourseEnrollmentModel>> fetchCourses() async {
    final uri = Uri.parse(ApiConfig.coursesEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => AcademicCourseEnrollmentModel.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load courses: ${response.body}');
    }
  }

  /// Events
  Future<List<AcademicEventModel>> fetchEvents({String? courseId, String? status}) async {
    final queryParams = <String, String>{};
    if (courseId != null) queryParams['course_id'] = courseId;
    if (status != null) queryParams['status'] = status;

    final uri = Uri.parse(ApiConfig.eventsEndpoint).replace(queryParameters: queryParams);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => AcademicEventModel.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load events: ${response.body}');
    }
  }

  Future<AcademicEventModel> createEvent({
    required String courseId,
    required String title,
    required String eventType,
    required DateTime dueAt,
    String? description,
    String priority = 'medium',
  }) async {
    final uri = Uri.parse(ApiConfig.eventsEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.post(
      uri,
      headers: headers,
      body: jsonEncode({
        'course_id': courseId,
        'title': title,
        'event_type': eventType,
        'due_at': dueAt.toUtc().toIso8601String(),
        'description': description,
        'priority': priority,
      }),
    );

    if (response.statusCode == 201) {
      return AcademicEventModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to create event');
    }
  }

  Future<AcademicEventModel> updateEvent(String eventId, Map<String, dynamic> updates) async {
    final uri = Uri.parse('${ApiConfig.eventsEndpoint}/$eventId');
    final headers = await authService.getAuthHeaders();
    final response = await client.patch(uri, headers: headers, body: jsonEncode(updates));

    if (response.statusCode == 200) {
      return AcademicEventModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to update event');
    }
  }

  Future<void> deleteEvent(String eventId) async {
    final uri = Uri.parse('${ApiConfig.eventsEndpoint}/$eventId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 204) {
      throw Exception('Failed to delete event');
    }
  }

  /// Tasks
  Future<List<TaskModel>> fetchTasks({String? courseId, String? status}) async {
    final queryParams = <String, String>{};
    if (courseId != null) queryParams['course_id'] = courseId;
    if (status != null) queryParams['status'] = status;

    final uri = Uri.parse(ApiConfig.tasksEndpoint).replace(queryParameters: queryParams);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => TaskModel.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load tasks: ${response.body}');
    }
  }

  Future<TaskModel> createTask({
    required String title,
    String? courseId,
    String? description,
    String priority = 'medium',
    int? estimatedMinutes,
    DateTime? dueDate,
  }) async {
    final uri = Uri.parse(ApiConfig.tasksEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.post(
      uri,
      headers: headers,
      body: jsonEncode({
        'title': title,
        'course_id': courseId,
        'description': description,
        'priority': priority,
        'estimated_minutes': estimatedMinutes,
        'due_date': dueDate?.toUtc().toIso8601String(),
      }),
    );

    if (response.statusCode == 201) {
      return TaskModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to create task');
    }
  }

  Future<TaskModel> updateTask(String taskId, Map<String, dynamic> updates) async {
    final uri = Uri.parse('${ApiConfig.tasksEndpoint}/$taskId');
    final headers = await authService.getAuthHeaders();
    final response = await client.patch(uri, headers: headers, body: jsonEncode(updates));

    if (response.statusCode == 200) {
      return TaskModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to update task');
    }
  }

  Future<void> deleteTask(String taskId) async {
    final uri = Uri.parse('${ApiConfig.tasksEndpoint}/$taskId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 204) {
      throw Exception('Failed to delete task');
    }
  }

  /// Study Sessions
  Future<List<StudySessionModel>> fetchStudySessions({String? courseId}) async {
    final queryParams = <String, String>{};
    if (courseId != null) queryParams['course_id'] = courseId;

    final uri = Uri.parse(ApiConfig.studySessionsEndpoint).replace(queryParameters: queryParams);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => StudySessionModel.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load study sessions: ${response.body}');
    }
  }

  Future<StudySessionModel> createStudySession({
    required DateTime scheduledStart,
    required DateTime scheduledEnd,
    String? courseId,
    String? topic,
    String? notes,
  }) async {
    final uri = Uri.parse(ApiConfig.studySessionsEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.post(
      uri,
      headers: headers,
      body: jsonEncode({
        'scheduled_start': scheduledStart.toUtc().toIso8601String(),
        'scheduled_end': scheduledEnd.toUtc().toIso8601String(),
        'course_id': courseId,
        'topic': topic,
        'notes': notes,
      }),
    );

    if (response.statusCode == 201) {
      return StudySessionModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to schedule study session');
    }
  }

  Future<StudySessionModel> updateStudySession(String sessionId, Map<String, dynamic> updates) async {
    final uri = Uri.parse('${ApiConfig.studySessionsEndpoint}/$sessionId');
    final headers = await authService.getAuthHeaders();
    final response = await client.patch(uri, headers: headers, body: jsonEncode(updates));

    if (response.statusCode == 200) {
      return StudySessionModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to update study session');
    }
  }

  Future<void> deleteStudySession(String sessionId) async {
    final uri = Uri.parse('${ApiConfig.studySessionsEndpoint}/$sessionId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 204) {
      throw Exception('Failed to delete study session');
    }
  }

  /// Goals
  Future<List<GoalModel>> fetchGoals({String? courseId, String? status}) async {
    final queryParams = <String, String>{};
    if (courseId != null) queryParams['course_id'] = courseId;
    if (status != null) queryParams['status'] = status;

    final uri = Uri.parse(ApiConfig.goalsEndpoint).replace(queryParameters: queryParams);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => GoalModel.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load goals: ${response.body}');
    }
  }

  Future<GoalModel> createGoal({
    required String title,
    required double targetValue,
    double currentValue = 0.0,
    String? courseId,
    String? description,
    DateTime? targetDate,
  }) async {
    final uri = Uri.parse(ApiConfig.goalsEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.post(
      uri,
      headers: headers,
      body: jsonEncode({
        'title': title,
        'target_value': targetValue,
        'current_value': currentValue,
        'course_id': courseId,
        'description': description,
        'target_date': targetDate?.toUtc().toIso8601String(),
      }),
    );

    if (response.statusCode == 201) {
      return GoalModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to create goal');
    }
  }

  Future<GoalModel> updateGoal(String goalId, Map<String, dynamic> updates) async {
    final uri = Uri.parse('${ApiConfig.goalsEndpoint}/$goalId');
    final headers = await authService.getAuthHeaders();
    final response = await client.patch(uri, headers: headers, body: jsonEncode(updates));

    if (response.statusCode == 200) {
      return GoalModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to update goal');
    }
  }

  Future<void> deleteGoal(String goalId) async {
    final uri = Uri.parse('${ApiConfig.goalsEndpoint}/$goalId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 204) {
      throw Exception('Failed to delete goal');
    }
  }

  /// Grades
  Future<List<GradeModel>> fetchGrades({String? courseId}) async {
    final queryParams = <String, String>{};
    if (courseId != null) queryParams['course_id'] = courseId;

    final uri = Uri.parse(ApiConfig.gradesEndpoint).replace(queryParameters: queryParams);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);

    if (response.statusCode == 200) {
      final List<dynamic> data = jsonDecode(response.body);
      return data.map((e) => GradeModel.fromJson(e)).toList();
    } else {
      throw Exception('Failed to load grades: ${response.body}');
    }
  }

  Future<GradeModel> createGrade({
    required String courseId,
    required String assessmentName,
    required double score,
    required double maxScore,
    String? assessmentType,
  }) async {
    final uri = Uri.parse(ApiConfig.gradesEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.post(
      uri,
      headers: headers,
      body: jsonEncode({
        'course_id': courseId,
        'assessment_name': assessmentName,
        'score': score,
        'max_score': maxScore,
        'assessment_type': assessmentType,
      }),
    );

    if (response.statusCode == 201) {
      return GradeModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to add grade record');
    }
  }

  Future<void> deleteGrade(String gradeId) async {
    final uri = Uri.parse('${ApiConfig.gradesEndpoint}/$gradeId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 204) {
      throw Exception('Failed to delete grade record');
    }
  }
}
