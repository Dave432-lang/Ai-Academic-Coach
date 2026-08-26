import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../models/academic_models.dart';
import '../../../services/academic_service.dart';
import '../../../services/auth_service.dart';

class StudySessionsScreen extends StatefulWidget {
  final AuthService authService;

  const StudySessionsScreen({super.key, required this.authService});

  @override
  State<StudySessionsScreen> createState() => _StudySessionsScreenState();
}

class _StudySessionsScreenState extends State<StudySessionsScreen> {
  late final AcademicService _academicService;
  late Future<List<StudySessionModel>> _sessionsFuture;

  @override
  void initState() {
    super.initState();
    _academicService = AcademicService(authService: widget.authService);
    _refreshSessions();
  }

  void _refreshSessions() {
    setState(() {
      _sessionsFuture = _academicService.fetchStudySessions();
    });
  }

  Future<void> _showAddSessionDialog() async {
    final topicController = TextEditingController();
    final notesController = TextEditingController();
    DateTime start = DateTime.now().add(const Duration(hours: 1));
    DateTime end = start.add(const Duration(hours: 2));

    await showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('Schedule Study Session'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                TextField(
                  controller: topicController,
                  decoration: const InputDecoration(labelText: 'Study Topic'),
                ),
                TextField(
                  controller: notesController,
                  decoration: const InputDecoration(labelText: 'Notes / Objectives'),
                ),
                const SizedBox(height: 12),
                Text('Start: ${DateFormat('yyyy-MM-dd HH:mm').format(start)}'),
                Text('End: ${DateFormat('yyyy-MM-dd HH:mm').format(end)}'),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () async {
                try {
                  await _academicService.createStudySession(
                    scheduledStart: start,
                    scheduledEnd: end,
                    topic: topicController.text.trim().isEmpty ? null : topicController.text.trim(),
                    notes: notesController.text.trim().isEmpty ? null : notesController.text.trim(),
                  );
                  if (ctx.mounted) Navigator.pop(ctx);
                  _refreshSessions();
                } catch (e) {
                  if (ctx.mounted) ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text(e.toString())));
                }
              },
              child: const Text('Schedule'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Study Sessions')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddSessionDialog,
        icon: const Icon(Icons.timer),
        label: const Text('Schedule Session'),
      ),
      body: RefreshIndicator(
        onRefresh: () async => _refreshSessions(),
        child: FutureBuilder<List<StudySessionModel>>(
          future: _sessionsFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }

            final sessions = snapshot.data ?? [];
            if (sessions.isEmpty) {
              return const Center(child: Text('No study sessions scheduled.'));
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: sessions.length,
              itemBuilder: (context, index) {
                final s = sessions[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12.0),
                  child: ListTile(
                    leading: const Icon(Icons.alarm, color: Colors.indigo),
                    title: Text(s.topic ?? 'General Study Session', style: const TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text('${DateFormat('MMM d, HH:mm').format(s.scheduledStart.toLocal())} - ${DateFormat('HH:mm').format(s.scheduledEnd.toLocal())}\nStatus: ${s.status.toUpperCase()}'),
                    trailing: IconButton(
                      icon: const Icon(Icons.delete_outline, color: Colors.red),
                      onPressed: () async {
                        await _academicService.deleteStudySession(s.id);
                        _refreshSessions();
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
