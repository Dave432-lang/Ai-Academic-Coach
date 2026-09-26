import 'dart:io' show Platform;
import 'package:flutter/foundation.dart' show kIsWeb;

class ApiConfig {
  /// Base API URL selection based on runtime environment & platform:
  ///
  /// - Android emulator: http://10.0.2.2:8000
  /// - Physical Android device: http://<LAN_IP>:8000 (Set custom Physical LAN IP below)
  /// - iOS simulator: http://localhost:8000
  /// - Windows desktop / macOS / Linux: http://localhost:8000
  /// - Web browser: http://localhost:8000
  
  static const String _defaultLocalhost = "http://localhost:8000";
  static const String _androidEmulatorUrl = "http://10.0.2.2:8000";
  
  // Replace with local machine IP (e.g., http://192.168.1.100:8000) when testing on physical devices
  static const String customPhysicalDeviceUrl = "http://192.168.1.100:8000";
  static const bool usePhysicalDeviceIp = false;

  static String get baseUrl {
    if (kIsWeb) {
      return _defaultLocalhost;
    }

    if (usePhysicalDeviceIp) {
      return customPhysicalDeviceUrl;
    }

    if (Platform.isAndroid) {
      return _androidEmulatorUrl;
    } else if (Platform.isIOS || Platform.isWindows || Platform.isMacOS || Platform.isLinux) {
      return _defaultLocalhost;
    }

    return _defaultLocalhost;
  }

  static String get healthEndpoint => "$baseUrl/health";

  // Auth endpoints
  static String get authSignupEndpoint => "$baseUrl/api/v1/auth/signup";
  static String get authLoginEndpoint => "$baseUrl/api/v1/auth/login";
  static String get authMeEndpoint => "$baseUrl/api/v1/auth/me";

  // Onboarding endpoints
  static String get onboardingStatusEndpoint => "$baseUrl/api/v1/onboarding/status";
  static String get universitiesEndpoint => "$baseUrl/api/v1/universities";
  static String get onboardingProfileEndpoint => "$baseUrl/api/v1/onboarding/profile";
  static String get onboardingCoursesEndpoint => "$baseUrl/api/v1/onboarding/courses";
  static String get onboardingCompleteEndpoint => "$baseUrl/api/v1/onboarding/complete";

  // Phase 4 Academic Management Endpoints
  static String get coursesEndpoint => "$baseUrl/api/v1/courses";
  static String get eventsEndpoint => "$baseUrl/api/v1/events";
  static String get tasksEndpoint => "$baseUrl/api/v1/tasks";
  static String get studySessionsEndpoint => "$baseUrl/api/v1/study-sessions";
  static String get goalsEndpoint => "$baseUrl/api/v1/goals";
  static String get gradesEndpoint => "$baseUrl/api/v1/grades";
  static String get dashboardSummaryEndpoint => "$baseUrl/api/v1/dashboard/summary";

  // Phase 5 Course Materials Endpoint
  static String get materialsEndpoint => "$baseUrl/api/v1/materials";

}
