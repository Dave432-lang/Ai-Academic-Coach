import 'package:flutter_test/flutter_test.dart';
import 'package:ai_academic_coach/main.dart';

void main() {
  testWidgets('App starts on WelcomeScreen and displays branding and auth action buttons', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const AiAcademicCoachApp());

    // Verify that title and welcome action buttons are displayed
    expect(find.text('AI Academic Coach'), findsOneWidget);
    expect(find.text('Get Started / Create Account'), findsOneWidget);
    expect(find.text('I already have an account'), findsOneWidget);
  });
}
