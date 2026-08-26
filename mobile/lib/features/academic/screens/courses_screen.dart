import 'package:flutter/material.dart';
import '../../../models/academic_models.dart';
import '../../../services/academic_service.dart';
import '../../../services/auth_service.dart';

class CoursesScreen extends StatefulWidget {
  final AuthService authService;

  const CoursesScreen({super.key, required this.authService});

  @override
  State<CoursesScreen> createState() => _CoursesScreenState();
}

class _CoursesScreenState extends State<CoursesScreen> {
  late final AcademicService _academicService;
  late Future<List<AcademicCourseEnrollmentModel>> _coursesFuture;

  @override
  void initState() {
    super.initState();
    _academicService = AcademicService(authService: widget.authService);
    _refreshCourses();
  }

  void _refreshCourses() {
    setState(() {
      _coursesFuture = _academicService.fetchCourses();
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Enrolled Courses'),
        elevation: 0,
      ),
      body: RefreshIndicator(
        onRefresh: () async => _refreshCourses(),
        child: FutureBuilder<List<AcademicCourseEnrollmentModel>>(
          future: _coursesFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }

            if (snapshot.hasError) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(24.0),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.error_outline, size: 48, color: colorScheme.error),
                      const SizedBox(height: 12),
                      Text(
                        'Failed to load courses',
                        style: theme.textTheme.titleMedium,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        snapshot.error.toString(),
                        textAlign: TextAlign.center,
                        style: theme.textTheme.bodySmall,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: _refreshCourses,
                        icon: const Icon(Icons.refresh),
                        label: const Text('Retry'),
                      ),
                    ],
                  ),
                ),
              );
            }

            final enrollments = snapshot.data ?? [];

            if (enrollments.isEmpty) {
              return const Center(
                child: Text('No active course enrollments found.'),
              );
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: enrollments.length,
              itemBuilder: (context, index) {
                final item = enrollments[index];
                final course = item.course;

                return Card(
                  elevation: 2,
                  margin: const EdgeInsets.only(bottom: 14.0),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(18.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(
                                color: colorScheme.primaryContainer,
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Text(
                                course.courseCode,
                                style: theme.textTheme.titleSmall?.copyWith(
                                  color: colorScheme.onPrimaryContainer,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                            const Spacer(),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: const Color(0xFF10B981).withValues(alpha: 0.15),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: const Text(
                                'ACTIVE',
                                style: TextStyle(
                                  color: Color(0xFF10B981),
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 12),
                        Text(
                          course.courseName,
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        if (course.description != null && course.description!.isNotEmpty) ...[
                          const SizedBox(height: 6),
                          Text(
                            course.description!,
                            style: theme.textTheme.bodyMedium?.copyWith(
                              color: colorScheme.onSurfaceVariant,
                            ),
                          ),
                        ],
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            Icon(Icons.credit_card, size: 16, color: colorScheme.secondary),
                            const SizedBox(width: 4),
                            Text(
                              '${course.creditHours ?? 3} Credit Hours',
                              style: theme.textTheme.bodySmall,
                            ),
                            if (item.semester != null) ...[
                              const SizedBox(width: 16),
                              Icon(Icons.calendar_month, size: 16, color: colorScheme.secondary),
                              const SizedBox(width: 4),
                              Text(
                                '${item.semester} (${item.academicYear ?? ""})',
                                style: theme.textTheme.bodySmall,
                              ),
                            ],
                          ],
                        ),
                      ],
                    ),
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}
