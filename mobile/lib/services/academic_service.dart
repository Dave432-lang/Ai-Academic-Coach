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

  /// Robust helper to parse JSON list responses and extract 401/error details safely
  static List<dynamic> _parseJsonList(http.Response response, String fallbackMessage) {
    dynamic body;
    try {
      body = jsonDecode(response.body);
    } catch (_) {
      throw Exception('$fallbackMessage (${response.statusCode})');
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (body is List) {
        return body;
      }
      throw Exception('Expected JSON list response from API');
    } else {
      if (body is Map && body.containsKey('detail')) {
        throw Exception(body['detail'].toString());
      }
      throw Exception('$fallbackMessage (${response.statusCode})');
    }
  }

  /// Robust helper to parse JSON map responses and extract 401/error details safely
  static Map<String, dynamic> _parseJsonMap(http.Response response, String fallbackMessage) {
    dynamic body;
    try {
      body = jsonDecode(response.body);
    } catch (_) {
      throw Exception('$fallbackMessage (${response.statusCode})');
    }

    if (response.statusCode >= 200 && response.statusCode < 300) {
      if (body is Map<String, dynamic>) {
        return body;
      }
      if (body is Map) {
        return Map<String, dynamic>.from(body);
      }
      throw Exception('Expected JSON object response from API');
    } else {
      if (body is Map && body.containsKey('detail')) {
        throw Exception(body['detail'].toString());
      }
      throw Exception('$fallbackMessage (${response.statusCode})');
    }
  }

  /// Dashboard Summary
  Future<DashboardSummaryModel> fetchDashboardSummary() async {
    final uri = Uri.parse(ApiConfig.dashboardSummaryEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);
    final map = _parseJsonMap(response, 'Failed to load dashboard summary');
    return DashboardSummaryModel.fromJson(map);
  }

  /// Courses
  Future<List<AcademicCourseEnrollmentModel>> fetchCourses() async {
    final uri = Uri.parse(ApiConfig.coursesEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);
    final list = _parseJsonList(response, 'Failed to load courses');
    return list.map((e) => AcademicCourseEnrollmentModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  /// Events
  Future<List<AcademicEventModel>> fetchEvents({String? courseId, String? status}) async {
    final queryParams = <String, String>{};
    if (courseId != null) queryParams['course_id'] = courseId;
    if (status != null) queryParams['status'] = status;

    final uri = Uri.parse(ApiConfig.eventsEndpoint).replace(queryParameters: queryParams);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);
    final list = _parseJsonList(response, 'Failed to load events');
    return list.map((e) => AcademicEventModel.fromJson(e as Map<String, dynamic>)).toList();
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
    final map = _parseJsonMap(response, 'Failed to create event');
    return AcademicEventModel.fromJson(map);
  }

  Future<AcademicEventModel> updateEvent(String eventId, Map<String, dynamic> updates) async {
    final uri = Uri.parse('${ApiConfig.eventsEndpoint}/$eventId');
    final headers = await authService.getAuthHeaders();
    final response = await client.patch(uri, headers: headers, body: jsonEncode(updates));
    final map = _parseJsonMap(response, 'Failed to update event');
    return AcademicEventModel.fromJson(map);
  }

  Future<void> deleteEvent(String eventId) async {
    final uri = Uri.parse('${ApiConfig.eventsEndpoint}/$eventId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 204) {
      _parseJsonMap(response, 'Failed to delete event');
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
    final list = _parseJsonList(response, 'Failed to load tasks');
    return list.map((e) => TaskModel.fromJson(e as Map<String, dynamic>)).toList();
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
    final map = _parseJsonMap(response, 'Failed to create task');
    return TaskModel.fromJson(map);
  }

  Future<TaskModel> updateTask(String taskId, Map<String, dynamic> updates) async {
    final uri = Uri.parse('${ApiConfig.tasksEndpoint}/$taskId');
    final headers = await authService.getAuthHeaders();
    final response = await client.patch(uri, headers: headers, body: jsonEncode(updates));
    final map = _parseJsonMap(response, 'Failed to update task');
    return TaskModel.fromJson(map);
  }

  Future<void> deleteTask(String taskId) async {
    final uri = Uri.parse('${ApiConfig.tasksEndpoint}/$taskId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 204) {
      _parseJsonMap(response, 'Failed to delete task');
    }
  }

  /// Study Sessions
  Future<List<StudySessionModel>> fetchStudySessions({String? courseId}) async {
    final queryParams = <String, String>{};
    if (courseId != null) queryParams['course_id'] = courseId;

    final uri = Uri.parse(ApiConfig.studySessionsEndpoint).replace(queryParameters: queryParams);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);
    final list = _parseJsonList(response, 'Failed to load study sessions');
    return list.map((e) => StudySessionModel.fromJson(e as Map<String, dynamic>)).toList();
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
    final map = _parseJsonMap(response, 'Failed to schedule study session');
    return StudySessionModel.fromJson(map);
  }

  Future<StudySessionModel> updateStudySession(String sessionId, Map<String, dynamic> updates) async {
    final uri = Uri.parse('${ApiConfig.studySessionsEndpoint}/$sessionId');
    final headers = await authService.getAuthHeaders();
    final response = await client.patch(uri, headers: headers, body: jsonEncode(updates));
    final map = _parseJsonMap(response, 'Failed to update study session');
    return StudySessionModel.fromJson(map);
  }

  Future<void> deleteStudySession(String sessionId) async {
    final uri = Uri.parse('${ApiConfig.studySessionsEndpoint}/$sessionId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 204) {
      _parseJsonMap(response, 'Failed to delete study session');
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
    final list = _parseJsonList(response, 'Failed to load goals');
    return list.map((e) => GoalModel.fromJson(e as Map<String, dynamic>)).toList();
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
    final map = _parseJsonMap(response, 'Failed to create goal');
    return GoalModel.fromJson(map);
  }

  Future<GoalModel> updateGoal(String goalId, Map<String, dynamic> updates) async {
    final uri = Uri.parse('${ApiConfig.goalsEndpoint}/$goalId');
    final headers = await authService.getAuthHeaders();
    final response = await client.patch(uri, headers: headers, body: jsonEncode(updates));
    final map = _parseJsonMap(response, 'Failed to update goal');
    return GoalModel.fromJson(map);
  }

  Future<void> deleteGoal(String goalId) async {
    final uri = Uri.parse('${ApiConfig.goalsEndpoint}/$goalId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 204) {
      _parseJsonMap(response, 'Failed to delete goal');
    }
  }

  /// Grades
  Future<List<GradeModel>> fetchGrades({String? courseId}) async {
    final queryParams = <String, String>{};
    if (courseId != null) queryParams['course_id'] = courseId;

    final uri = Uri.parse(ApiConfig.gradesEndpoint).replace(queryParameters: queryParams);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);
    final list = _parseJsonList(response, 'Failed to load grades');
    return list.map((e) => GradeModel.fromJson(e as Map<String, dynamic>)).toList();
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
    final map = _parseJsonMap(response, 'Failed to add grade record');
    return GradeModel.fromJson(map);
  }

  Future<void> deleteGrade(String gradeId) async {
    final uri = Uri.parse('${ApiConfig.gradesEndpoint}/$gradeId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 204) {
      _parseJsonMap(response, 'Failed to delete grade record');
    }
  }

  /// Course Materials
  Future<List<CourseMaterialModel>> fetchMaterials({String? courseId}) async {
    final queryParams = <String, String>{};
    if (courseId != null && courseId.isNotEmpty) queryParams['course_id'] = courseId;

    final uri = Uri.parse(ApiConfig.materialsEndpoint).replace(queryParameters: queryParams);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);
    final list = _parseJsonList(response, 'Failed to load materials');
    return list.map((e) => CourseMaterialModel.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<CourseMaterialModel> uploadMaterial({
    required String courseId,
    required List<int> fileBytes,
    required String fileName,
    String? title,
  }) async {
    final uri = Uri.parse(ApiConfig.materialsEndpoint);
    final authHeaders = await authService.getAuthHeaders();

    final request = http.MultipartRequest('POST', uri);
    request.headers.addAll(authHeaders);
    request.fields['course_id'] = courseId;
    if (title != null && title.isNotEmpty) {
      request.fields['title'] = title;
    }

    final multipartFile = http.MultipartFile.fromBytes(
      'file',
      fileBytes,
      filename: fileName,
    );
    request.files.add(multipartFile);

    final streamedResponse = await client.send(request);
    final response = await http.Response.fromStream(streamedResponse);
    final map = _parseJsonMap(response, 'Failed to upload material');
    return CourseMaterialModel.fromJson(map);
  }

  Future<List<int>> downloadMaterialBytes(String materialId) async {
    final uri = Uri.parse('${ApiConfig.materialsEndpoint}/$materialId/download');
    final headers = await authService.getAuthHeaders();
    final response = await client.get(uri, headers: headers);

    if (response.statusCode == 200) {
      return response.bodyBytes;
    } else {
      _parseJsonMap(response, 'Failed to download material');
      return [];
    }
  }

  Future<String> getMaterialDownloadUrl(String materialId) async {
    final token = await authService.getAuthToken();
    final baseUrl = '${ApiConfig.materialsEndpoint}/$materialId/download';
    if (token != null && token.isNotEmpty) {
      return '$baseUrl?token=$token';
    }
    return baseUrl;
  }

  Future<void> deleteMaterial(String materialId) async {
    final uri = Uri.parse('${ApiConfig.materialsEndpoint}/$materialId');
    final headers = await authService.getAuthHeaders();
    final response = await client.delete(uri, headers: headers);

    if (response.statusCode != 200) {
      _parseJsonMap(response, 'Failed to delete material');
    }
  }
}
