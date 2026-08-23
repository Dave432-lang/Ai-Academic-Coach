import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:ai_academic_coach/services/auth_service.dart';
import 'package:ai_academic_coach/services/onboarding_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  FlutterSecureStorage.setMockInitialValues({});

  group('AuthService Tests', () {
    test('signup success parses TokenModel and sets authToken securely', () async {
      final mockClient = MockClient((request) async {
        if (request.url.path.contains('/signup')) {
          return http.Response(
            jsonEncode({
              'access_token': 'jwt_test_token_123',
              'token_type': 'bearer',
              'user': {
                'id': '11111111-1111-1111-1111-111111111111',
                'email': 'test@example.com',
                'account_status': 'active',
                'onboarding_completed': false,
                'created_at': DateTime.now().toIso8601String(),
              }
            }),
            201,
          );
        }
        return http.Response('Not found', 404);
      });

      final authService = AuthService(client: mockClient);
      final result = await authService.signup(email: 'test@example.com', password: 'password123');

      expect(result['success'], isTrue);
      expect(await authService.getAuthToken(), 'jwt_test_token_123');
      final headers = await authService.getAuthHeaders();
      expect(headers['Authorization'], 'Bearer jwt_test_token_123');
    });

    test('login invalid credentials handles error message cleanly', () async {
      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({'detail': 'Invalid email or password'}),
          401,
        );
      });

      final authService = AuthService(client: mockClient);
      final result = await authService.login(email: 'wrong@example.com', password: 'wrong');

      expect(result['success'], isFalse);
      expect(result['statusCode'], 401);
      expect(result['error'], 'Invalid email or password');
    });
  });

  group('OnboardingService Tests', () {
    test('getOnboardingStatus parses missing requirements correctly', () async {
      final authService = AuthService();
      await authService.setAuthToken('test_token');

      final mockClient = MockClient((request) async {
        return http.Response(
          jsonEncode({
            'onboarding_completed': false,
            'has_profile': true,
            'has_university': true,
            'has_academic_info': true,
            'active_course_count': 0,
            'missing_requirements': ['At least one active course enrollment'],
          }),
          200,
        );
      });

      final onboardingService = OnboardingService(authService: authService, client: mockClient);
      final statusModel = await onboardingService.getOnboardingStatus();

      expect(statusModel.onboardingCompleted, isFalse);
      expect(statusModel.activeCourseCount, 0);
      expect(statusModel.missingRequirements, contains('At least one active course enrollment'));
    });
  });
}
