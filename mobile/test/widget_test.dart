import 'package:flutter_test/flutter_test.dart';
import 'package:ai_academic_coach/main.dart';

void main() {
  testWidgets('App starts and displays title and foundation message', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const AiAcademicCoachApp());

    // Verify that title and foundation text are displayed
    expect(find.text('AI Academic Coach'), findsOneWidget);
    expect(find.text('Foundation setup complete.'), findsOneWidget);
    expect(find.text('Phase 1 Architecture'), findsOneWidget);
  });
}
