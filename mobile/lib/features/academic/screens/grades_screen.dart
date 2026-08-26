import 'package:flutter/material.dart';
import '../../../models/academic_models.dart';
import '../../../services/academic_service.dart';
import '../../../services/auth_service.dart';

class GradesScreen extends StatefulWidget {
  final AuthService authService;

  const GradesScreen({super.key, required this.authService});

  @override
  State<GradesScreen> createState() => _GradesScreenState();
}

class _GradesScreenState extends State<GradesScreen> {
  late final AcademicService _academicService;
  late Future<List<GradeModel>> _gradesFuture;
  List<AcademicCourseEnrollmentModel> _courses = [];

  @override
  void initState() {
    super.initState();
    _academicService = AcademicService(authService: widget.authService);
    _loadCourses();
    _refreshGrades();
  }

  Future<void> _loadCourses() async {
    try {
      final courses = await _academicService.fetchCourses();
      if (mounted) setState(() => _courses = courses);
    } catch (_) {}
  }

  void _refreshGrades() {
    setState(() {
      _gradesFuture = _academicService.fetchGrades();
    });
  }

  Future<void> _showAddGradeDialog() async {
    if (_courses.isEmpty) await _loadCourses();
    if (_courses.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please enroll in a course first.')),
        );
      }
      return;
    }

    final nameController = TextEditingController();
    final scoreController = TextEditingController();
    final maxScoreController = TextEditingController(text: '100');
    String selectedCourse = _courses.first.courseId;
    String selectedType = 'quiz';

    await showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Add Grade Record'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                DropdownButtonFormField<String>(
                  initialValue: selectedCourse,
                  decoration: const InputDecoration(labelText: 'Course'),
                  items: _courses
                      .map((c) => DropdownMenuItem(
                            value: c.courseId,
                            child: Text(c.course.courseCode),
                          ))
                      .toList(),
                  onChanged: (val) => setDialogState(() => selectedCourse = val!),
                ),
                TextField(
                  controller: nameController,
                  decoration: const InputDecoration(labelText: 'Assessment Name (e.g. Quiz 1)'),
                ),
                DropdownButtonFormField<String>(
                  initialValue: selectedType,
                  decoration: const InputDecoration(labelText: 'Type'),
                  items: ['quiz', 'assignment', 'midterm', 'final_exam', 'project']
                      .map((t) => DropdownMenuItem(value: t, child: Text(t.toUpperCase())))
                      .toList(),
                  onChanged: (val) => setDialogState(() => selectedType = val!),
                ),
                TextField(
                  controller: scoreController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Score Obtained'),
                ),
                TextField(
                  controller: maxScoreController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Max Score'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () async {
                if (nameController.text.trim().isEmpty || scoreController.text.trim().isEmpty) return;
                try {
                  final score = double.parse(scoreController.text.trim());
                  final maxScore = double.parse(maxScoreController.text.trim());
                  if (score > maxScore) {
                    ScaffoldMessenger.of(ctx).showSnackBar(
                      const SnackBar(content: Text('Score cannot exceed max score')),
                    );
                    return;
                  }

                  await _academicService.createGrade(
                    courseId: selectedCourse,
                    assessmentName: nameController.text.trim(),
                    score: score,
                    maxScore: maxScore,
                    assessmentType: selectedType,
                  );
                  if (ctx.mounted) Navigator.pop(ctx);
                  _refreshGrades();
                } catch (e) {
                  if (ctx.mounted) ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text(e.toString())));
                }
              },
              child: const Text('Save Grade'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Grades & Performance')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddGradeDialog,
        icon: const Icon(Icons.grade),
        label: const Text('Add Grade'),
      ),
      body: RefreshIndicator(
        onRefresh: () async => _refreshGrades(),
        child: FutureBuilder<List<GradeModel>>(
          future: _gradesFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }

            final grades = snapshot.data ?? [];
            if (grades.isEmpty) {
              return const Center(child: Text('No grade records entered.'));
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: grades.length,
              itemBuilder: (context, index) {
                final g = grades[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12.0),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: Colors.indigo.shade100,
                      child: Text(
                        '${(g.percentage ?? 0).toStringAsFixed(0)}%',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                      ),
                    ),
                    title: Text(g.assessmentName, style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text('Score: ${g.score} / ${g.maxScore} (${g.assessmentType?.toUpperCase() ?? "OTHER"})'),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete_outline, color: Colors.red),
                      onPressed: () async {
                        await _academicService.deleteGrade(g.id);
                        _refreshGrades();
                      },
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
