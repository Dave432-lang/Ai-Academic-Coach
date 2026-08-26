import 'package:flutter/material.dart';
import '../../../models/academic_models.dart';
import '../../../services/academic_service.dart';
import '../../../services/auth_service.dart';

class TasksScreen extends StatefulWidget {
  final AuthService authService;

  const TasksScreen({super.key, required this.authService});

  @override
  State<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends State<TasksScreen> {
  late final AcademicService _academicService;
  late Future<List<TaskModel>> _tasksFuture;
  List<AcademicCourseEnrollmentModel> _courses = [];

  @override
  void initState() {
    super.initState();
    _academicService = AcademicService(authService: widget.authService);
    _loadCourses();
    _refreshTasks();
  }

  Future<void> _loadCourses() async {
    try {
      final courses = await _academicService.fetchCourses();
      if (mounted) setState(() => _courses = courses);
    } catch (_) {}
  }

  void _refreshTasks() {
    setState(() {
      _tasksFuture = _academicService.fetchTasks();
    });
  }

  Future<void> _showAddTaskDialog() async {
    final titleController = TextEditingController();
    final descriptionController = TextEditingController();
    final minutesController = TextEditingController(text: '60');
    String? selectedCourseId = _courses.isNotEmpty ? _courses.first.courseId : null;
    String priority = 'medium';

    await showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Create Academic Task'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: titleController,
                  decoration: const InputDecoration(labelText: 'Task Title'),
                ),
                if (_courses.isNotEmpty)
                  DropdownButtonFormField<String>(
                    initialValue: selectedCourseId,
                    decoration: const InputDecoration(labelText: 'Course (Optional)'),
                    items: _courses
                        .map((c) => DropdownMenuItem(
                              value: c.courseId,
                              child: Text(c.course.courseCode),
                            ))
                        .toList(),
                    onChanged: (val) => setDialogState(() => selectedCourseId = val),
                  ),
                DropdownButtonFormField<String>(
                  initialValue: priority,
                  decoration: const InputDecoration(labelText: 'Priority'),
                  items: ['low', 'medium', 'high', 'critical']
                      .map((p) => DropdownMenuItem(value: p, child: Text(p.toUpperCase())))
                      .toList(),
                  onChanged: (val) => setDialogState(() => priority = val!),
                ),
                TextField(
                  controller: minutesController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(labelText: 'Est. Minutes'),
                ),
                TextField(
                  controller: descriptionController,
                  decoration: const InputDecoration(labelText: 'Description (Optional)'),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () async {
                if (titleController.text.trim().isEmpty) return;
                try {
                  await _academicService.createTask(
                    title: titleController.text.trim(),
                    courseId: selectedCourseId,
                    description: descriptionController.text.trim().isEmpty ? null : descriptionController.text.trim(),
                    priority: priority,
                    estimatedMinutes: int.tryParse(minutesController.text.trim()),
                  );
                  if (ctx.mounted) Navigator.pop(ctx);
                  _refreshTasks();
                } catch (e) {
                  if (ctx.mounted) ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text(e.toString())));
                }
              },
              child: const Text('Save Task'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Study Tasks')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddTaskDialog,
        icon: const Icon(Icons.check_box),
        label: const Text('Add Task'),
      ),
      body: RefreshIndicator(
        onRefresh: () async => _refreshTasks(),
        child: FutureBuilder<List<TaskModel>>(
          future: _tasksFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }

            if (snapshot.hasError) {
              return Center(child: Text('Error: ${snapshot.error}'));
            }

            final tasks = snapshot.data ?? [];
            if (tasks.isEmpty) {
              return const Center(child: Text('No active tasks found.'));
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: tasks.length,
              itemBuilder: (context, index) {
                final task = tasks[index];
                final isDone = task.status == 'completed';

                return Card(
                  margin: const EdgeInsets.only(bottom: 12.0),
                  child: CheckboxListTile(
                    value: isDone,
                    onChanged: (val) async {
                      final newStatus = (val ?? false) ? 'completed' : 'pending';
                      await _academicService.updateTask(task.id, {'status': newStatus});
                      _refreshTasks();
                    },
                    title: Text(
                      task.title,
                      style: TextStyle(
                        decoration: isDone ? TextDecoration.lineThrough : null,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    subtitle: Text('Priority: ${task.priority.toUpperCase()} | Est: ${task.estimatedMinutes ?? 0}m'),
                    secondary: IconButton(
                      icon: const Icon(Icons.delete_outline, color: Colors.red),
                      onPressed: () async {
                        await _academicService.deleteTask(task.id);
                        _refreshTasks();
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
