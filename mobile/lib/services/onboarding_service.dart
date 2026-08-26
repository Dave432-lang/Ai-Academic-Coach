import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/config/api_config.dart';
import '../models/onboarding_model.dart';
import 'auth_service.dart';

class OnboardingService {
  final http.Client client;
  final AuthService authService;

  OnboardingService({
    required this.authService,
    http.Client? client,
  }) : client = client ?? http.Client();

  /// Search universities by keyword
  Future<List<UniversityModel>> searchUniversities({String? search, int limit = 20}) async {
    final queryParams = <String, String>{
      'limit': limit.toString(),
    };
    if (search != null && search.trim().isNotEmpty) {
      queryParams['search'] = search.trim();
    }

    final uri = Uri.parse(ApiConfig.universitiesEndpoint).replace(queryParameters: queryParams);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(
      uri,
      headers: headers,
    );

    if (response.statusCode == 200) {
      final List<dynamic> list = jsonDecode(response.body);
      return list.map((item) => UniversityModel.fromJson(item as Map<String, dynamic>)).toList();
    } else {
      throw Exception('Failed to search universities: ${response.body}');
    }
  }

  /// Create a new university
  Future<UniversityModel> createUniversity({
    required String name,
    required String country,
    String? website,
    String? timezone,
  }) async {
    final uri = Uri.parse(ApiConfig.universitiesEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.post(
      uri,
      headers: headers,
      body: jsonEncode({
        'name': name.trim(),
        'country': country.trim(),
        'website': website?.trim(),
        'timezone': timezone?.trim(),
      }),
    );

    if (response.statusCode == 200 || response.statusCode == 201) {
      return UniversityModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to create university');
    }
  }

  /// Retrieve onboarding status
  Future<OnboardingStatusModel> getOnboardingStatus() async {
    final uri = Uri.parse(ApiConfig.onboardingStatusEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.get(
      uri,
      headers: headers,
    );

    if (response.statusCode == 200) {
      return OnboardingStatusModel.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to retrieve onboarding status: ${response.body}');
    }
  }

  /// Update student profile
  Future<StudentProfileModel> updateProfile({
    required String fullName,
    String? country,
    String timezone = 'UTC',
    String? universityId,
    String? program,
    String? level,
    String? academicYear,
    String? semester,
  }) async {
    final uri = Uri.parse(ApiConfig.onboardingProfileEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.post(
      uri,
      headers: headers,
      body: jsonEncode({
        'full_name': fullName,
        'country': country,
        'timezone': timezone,
        'university_id': universityId,
        'program': program,
        'level': level,
        'academic_year': academicYear,
        'semester': semester,
      }),
    );

    if (response.statusCode == 200) {
      return StudentProfileModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to update profile');
    }
  }

  /// Add course and register enrollment
  Future<CourseEnrollmentModel> addCourseAndEnroll({
    required String courseCode,
    required String courseName,
    String? description,
    int? creditHours,
    String? academicYear,
    String? semester,
  }) async {
    final uri = Uri.parse(ApiConfig.onboardingCoursesEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.post(
      uri,
      headers: headers,
      body: jsonEncode({
        'course_code': courseCode,
        'course_name': courseName,
        'description': description,
        'credit_hours': creditHours,
        'academic_year': academicYear,
        'semester': semester,
      }),
    );

    if (response.statusCode == 201) {
      return CourseEnrollmentModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to add course enrollment');
    }
  }

  /// Complete onboarding flow
  Future<StudentProfileModel> completeOnboarding() async {
    final uri = Uri.parse(ApiConfig.onboardingCompleteEndpoint);
    final headers = await authService.getAuthHeaders();
    final response = await client.post(
      uri,
      headers: headers,
    );

    if (response.statusCode == 200) {
      return StudentProfileModel.fromJson(jsonDecode(response.body));
    } else {
      final body = jsonDecode(response.body);
      throw Exception(body['detail'] ?? 'Failed to complete onboarding');
    }
  }
}
