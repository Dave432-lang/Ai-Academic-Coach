import 'package:flutter/material.dart';
import '../features/auth/login_screen.dart';
import '../features/auth/signup_screen.dart';
import '../features/auth/welcome_screen.dart';
import '../features/home/screens/home_screen.dart';
import '../features/onboarding/onboarding_screen.dart';
import '../features/materials/screens/materials_screen.dart';

class AppRoutes {
  static const String welcome = '/welcome';
  static const String signup = '/signup';
  static const String login = '/login';
  static const String onboarding = '/onboarding';
  static const String home = '/home';
  static const String materials = '/materials';

  static Map<String, WidgetBuilder> get routes => {
        welcome: (context) => const WelcomeScreen(),
        signup: (context) => const SignupScreen(),
        login: (context) => const LoginScreen(),
        onboarding: (context) => const OnboardingScreen(),
        home: (context) => const HomeScreen(),
        materials: (context) => const MaterialsScreen(),
      };
}
