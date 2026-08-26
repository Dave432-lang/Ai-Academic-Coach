import 'package:flutter/material.dart';
import '../../../models/academic_models.dart';
import '../../../services/academic_service.dart';
import '../../../services/auth_service.dart';

class GoalsScreen extends StatefulWidget {
  final AuthService authService;

  const GoalsScreen({super.key, required this.authService});

  @override
  State<GoalsScreen> createState() => _GoalsScreenState();
}

class _GoalsScreenState extends State<GoalsScreen> {
  late final AcademicService _academicService;
  late Future<List<GoalModel>> _goalsFuture;

  @override
  void initState() {
    super.initState();
    _academicService = AcademicService(authService: widget.authService);
    _refreshGoals();
  }

  void _refreshGoals() {
    setState(() {
      _goalsFuture = _academicService.fetchGoals();
    });
  }

  Future<void> _showAddGoalDialog() async {
    final titleController = TextEditingController();
    final targetController = TextEditingController(text: '85.0');
    final currentController = TextEditingController(text: '0.0');

    await showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Add Academic Goal'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: titleController,
              decoration: const InputDecoration(labelText: 'Goal Title (e.g. Target Grade A)'),
            ),
            TextField(
              controller: targetController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Target Value (%)'),
            ),
            TextField(
              controller: currentController,
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: 'Current Value (%)'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              if (titleController.text.trim().isEmpty) return;
              try {
                await _academicService.createGoal(
                  title: titleController.text.trim(),
                  targetValue: double.parse(targetController.text.trim()),
                  currentValue: double.parse(currentController.text.trim()),
                );
                if (ctx.mounted) Navigator.pop(ctx);
                _refreshGoals();
              } catch (e) {
                if (ctx.mounted) ScaffoldMessenger.of(ctx).showSnackBar(SnackBar(content: Text(e.toString())));
              }
            },
            child: const Text('Save Goal'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Academic Goals')),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showAddGoalDialog,
        icon: const Icon(Icons.flag),
        label: const Text('Add Goal'),
      ),
      body: RefreshIndicator(
        onRefresh: () async => _refreshGoals(),
        child: FutureBuilder<List<GoalModel>>(
          future: _goalsFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }

            final goals = snapshot.data ?? [];
            if (goals.isEmpty) {
              return const Center(child: Text('No active academic goals.'));
            }

            return ListView.builder(
              padding: const EdgeInsets.all(16.0),
              itemCount: goals.length,
              itemBuilder: (context, index) {
                final g = goals[index];
                final progress = g.targetValue > 0 ? (g.currentValue / g.targetValue).clamp(0.0, 1.0) : 0.0;

                return Card(
                  margin: const EdgeInsets.only(bottom: 12.0),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(g.title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                            const Spacer(),
                            IconButton(
                              icon: const Icon(Icons.delete_outline, color: Colors.red),
                              onPressed: () async {
                                await _academicService.deleteGoal(g.id);
                                _refreshGoals();
                              },
                            ),
                          ],
                        ),
                        const SizedBox(height: 8),
                        LinearProgressIndicator(value: progress, minHeight: 8),
                        const SizedBox(height: 8),
                        Text('Progress: ${g.currentValue} / ${g.targetValue} (${(progress * 100).toStringAsFixed(1)}%)'),
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
