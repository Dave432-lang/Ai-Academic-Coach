import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../models/academic_models.dart';
import '../../../services/academic_service.dart';
import '../../../services/auth_service.dart';

class EventsScreen extends StatefulWidget {
  final AuthService authService;

  const EventsScreen({super.key, required this.authService});

  @override
  State<EventsScreen> createState() => _EventsScreenState();
}

class _EventsScreenState extends State<EventsScreen> {
  late final AcademicService _academicService;
  late Future<List<AcademicEventModel>> _eventsFuture;
  List<AcademicCourseEnrollmentModel> _courses = [];
  String? _selectedCourseId;

  @override
  void initState() {
    super.initState();
    _academicService = AcademicService(authService: widget.authService);
    _loadCourses();
    _refreshEvents();
  }

  Future<void> _loadCourses() async {
    try {
      final courses = await _academicService.fetchCourses();
      if (mounted) {
        setState(() {
          _courses = courses;
        });
      }
    } catch (_) {}
  }

  void _refreshEvents() {
    setState(() {
      _eventsFuture = _academicService.fetchEvents(courseId: _selectedCourseId);
    });
  }

  Future<void> _showAddEventDialog() async {
    if (_courses.isEmpty) {
      await _loadCourses();
    }
    if (_courses.isEmpty) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Please enroll in a course first.')),
        );
      }
      return;
    }

    final titleController = TextEditingController();
    final descriptionController = TextEditingController();
    String selectedCourse = _selectedCourseId ?? _courses.first.courseId;
    String selectedType = 'assignment';
    String selectedPriority = 'medium';
    DateTime selectedDate = DateTime.now().add(const Duration(days: 3));

    await showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Add Academic Event'),
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
                            child: Text('${c.course.courseCode} - ${c.course.courseName}'),
                          ))
                      .toList(),
                  onChanged: (val) => setDialogState(() => selectedCourse = val!),
                ),
                TextField(
                  controller: titleController,
                  decoration: const InputDecoration(labelText: 'Title (e.g. Midterm Exam)'),
                ),
                DropdownButtonFormField<String>(
                  initialValue: selectedType,
                  decoration: const InputDecoration(labelText: 'Event Type'),
                  items: ['assignment', 'exam', 'quiz', 'presentation', 'project']
                      .map((t) => DropdownMenuItem(value: t, child: Text(t.toUpperCase())))
                      .toList(),
                  onChanged: (val) => setDialogState(() => selectedType = val!),
                ),
                DropdownButtonFormField<String>(
                  initialValue: selectedPriority,
                  decoration: const InputDecoration(labelText: 'Priority'),
                  items: ['low', 'medium', 'high', 'critical']
                      .map((p) => DropdownMenuItem(value: p, child: Text(p.toUpperCase())))
                      .toList(),
                  onChanged: (val) => setDialogState(() => selectedPriority = val!),
                ),
                TextField(
                  controller: descriptionController,
                  decoration: const InputDecoration(labelText: 'Description (Optional)'),
                ),
                const SizedBox(height: 12),
                ListTile(
                  title: Text('Due Date: ${DateFormat('yyyy-MM-dd HH:mm').format(selectedDate)}'),
                  trailing: const Icon(Icons.calendar_today),
                  onTap: () async {
                    final picked = await showDatePicker(
                      context: context,
                      initialDate: selectedDate,
                      firstDate: DateTime.now(),
                      lastDate: DateTime.now().add(const Duration(days: 365)),
                    );
                    if (picked != null) {
                      setDialogState(() => selectedDate = picked);
                    }
                  },
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                if (titleController.text.trim().isEmpty) return;
                try {
                  await _academicService.createEvent(
                    courseId: selectedCourse,
                    title: titleController.text.trim(),
                    eventType: selectedType,
                    dueAt: selectedDate,
                    description: descriptionController.text.trim().isEmpty ? null : descriptionController.text.trim(),
                    priority: selectedPriority,
                  );
                  if (ctx.mounted) Navigator.pop(ctx);
                  _refreshEvents();
                } catch (e) {
                  if (ctx.mounted) {
                    ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text(e.toString())));
                  }
                }
              },
              child: const Text('Save Event'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Academic Events & Schedule'),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddEventDialog,
        icon: const Icon(Icons.add),
        label: const Text('Add Event'),
      ),
      body: RefreshIndicator(
        onRefresh: () async => _refreshEvents(),
        child: FutureBuilder<List<AcademicEventModel>>(
          future: _eventsFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }

            if (snapshot.hasError) {
              return Center(child: Text('Error: ${snapshot.error}'));
            }

            final events = snapshot.data ?? [];
            if (events.isEmpty) {
              return const Center(child: Text('No upcoming academic events scheduled.'));
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: events.length,
              itemBuilder: (context, index) {
                final ev = events[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12.0),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16.0),
                    leading: CircleAvatar(
                      backgroundColor: theme.colorScheme.primaryContainer,
                      child: Icon(
                        ev.eventType == 'exam' ? Icons.quiz : Icons.assignment,
                        color: theme.colorScheme.onPrimaryContainer,
                      ),
                    ),
                    title: Text(ev.title, style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 4),
                        Text('Due: ${DateFormat('EEE, MMM d, yyyy @ HH:mm').format(ev.dueAt.toLocal())}'),
                        Text('Type: ${ev.eventType.toUpperCase()} | Priority: ${ev.priority.toUpperCase()}'),
                      ],
                    ),
                    trailing: PopupMenuButton<String>(
                      onSelected: (val) async {
                        if (val == 'delete') {
                          await _academicService.deleteEvent(ev.id);
                          _refreshEvents();
                        } else if (val == 'complete') {
                          await _academicService.updateEvent(ev.id, {'status': 'completed'});
                          _refreshEvents();
                        }
                      },
                      itemBuilder: (ctx) => [
                        const PopupMenuItem(value: 'complete', child: Text('Mark Completed')),
                        const PopupMenuItem(value: 'delete', child: Text('Delete Event', style: TextStyle(color: Colors.red))),
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
