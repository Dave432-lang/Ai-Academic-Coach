import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:ai_academic_coach/models/academic_models.dart';
import 'package:ai_academic_coach/features/materials/screens/materials_screen.dart';

void main() {
  group('CourseMaterialModel Tests', () {
    test('fromJson parses course material json correctly', () {
      final json = {
        'id': '11111111-1111-1111-1111-111111111111',
        'student_id': '22222222-2222-2222-2222-222222222222',
        'course_id': '33333333-3333-3333-3333-333333333333',
        'file_name': 'Syllabus.pdf',
        'file_type': 'application/pdf',
        'storage_key': 'student/course/file.pdf',
        'file_size': 1048576,
        'processing_status': 'pending',
        'created_at': '2026-08-26T10:00:00Z',
        'updated_at': '2026-08-26T10:00:00Z',
        'course_code': 'CS101',
        'course_name': 'Intro to Computer Science',
      };

      final model = CourseMaterialModel.fromJson(json);

      expect(model.id, '11111111-1111-1111-1111-111111111111');
      expect(model.fileName, 'Syllabus.pdf');
      expect(model.fileType, 'application/pdf');
      expect(model.fileSize, 1048576);
      expect(model.processingStatus, 'pending');
      expect(model.courseCode, 'CS101');
      expect(model.courseName, 'Intro to Computer Science');
    });
  });

  group('MaterialsScreen Widget Tests', () {
    testWidgets('Renders MaterialsScreen title and loading state', (WidgetTester tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: MaterialsScreen(),
        ),
      );

      expect(find.text('Course Materials'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });
  });
}
