import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';
import '../../../models/academic_models.dart';
import '../../../routes/app_routes.dart';
import '../../../services/academic_service.dart';
import '../../../services/api_service.dart';
import '../../../services/auth_service.dart';
import '../../academic/screens/courses_screen.dart';
import '../../academic/screens/events_screen.dart';
import '../../academic/screens/tasks_screen.dart';
import '../../academic/screens/study_sessions_screen.dart';
import '../../academic/screens/goals_screen.dart';
import '../../academic/screens/grades_screen.dart';

class HomeScreen extends StatefulWidget {
  final AuthService? authService;

  const HomeScreen({super.key, this.authService});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  late final AuthService _authService;
  late final AcademicService _academicService;

  bool _isLoadingHealth = false;
  String? _healthResult;
  bool _isSuccess = false;

  Map<String, dynamic>? _userMeData;
  bool _isLoadingMe = true;

  DashboardSummaryModel? _dashboardSummary;
  bool _isLoadingSummary = true;
  String? _summaryError;

  @override
  void initState() {
    super.initState();
    _authService = widget.authService ?? AuthService();
    _academicService = AcademicService(authService: _authService);
    _loadUserData();
    _loadDashboardSummary();
  }

  Future<void> _loadUserData() async {
    final result = await _authService.getMe();
    if (!mounted) return;
    setState(() {
      _isLoadingMe = false;
      if (result['success'] == true) {
        _userMeData = result['user'];
      }
    });
  }

  Future<void> _loadDashboardSummary() async {
    setState(() {
      _isLoadingSummary = true;
      _summaryError = null;
    });

    try {
      final summary = await _academicService.fetchDashboardSummary();
      if (!mounted) return;
      setState(() {
        _dashboardSummary = summary;
        _isLoadingSummary = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _summaryError = e.toString();
        _isLoadingSummary = false;
      });
    }
  }

  Future<void> _handleLogout() async {
    await _authService.logout();
    if (!mounted) return;
    Navigator.pushNamedAndRemoveUntil(context, AppRoutes.welcome, (route) => false);
  }

  Future<void> _verifyBackendHealth() async {
    setState(() {
      _isLoadingHealth = true;
      _healthResult = null;
    });

    final result = await _apiService.checkHealth();

    setState(() {
      _isLoadingHealth = false;
      _isSuccess = result["success"] == true;
      if (_isSuccess) {
        _healthResult = "Backend Status: OK (HTTP ${result['statusCode']})";
      } else {
        _healthResult = "Connection Info: ${result['error']}";
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Academic Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            tooltip: 'Refresh Dashboard',
            onPressed: () {
              _loadUserData();
              _loadDashboardSummary();
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'Log Out',
            onPressed: _handleLogout,
          ),
        ],
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFF0F172A),
              Color(0xFF1E1E38),
              Color(0xFF0F172A),
            ],
          ),
        ),
        child: SafeArea(
          child: RefreshIndicator(
            onRefresh: () async {
              await _loadUserData();
              await _loadDashboardSummary();
            },
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // User Welcome Card
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: AppTheme.surfaceColor,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: AppTheme.primaryColor.withValues(alpha: 0.4)),
                    ),
                    child: _isLoadingMe
                        ? const Center(child: CircularProgressIndicator(strokeWidth: 2))
                        : Row(
                            children: [
                              const CircleAvatar(
                                radius: 24,
                                backgroundColor: AppTheme.primaryColor,
                                child: Icon(Icons.person, color: Colors.white, size: 28),
                              ),
                              const SizedBox(width: 14),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(
                                      _dashboardSummary?.studentName ?? _userMeData?['email'] ?? 'Student',
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.white),
                                    ),
                                    const SizedBox(height: 4),
                                    Text(
                                      'Account: ${_userMeData?['account_status'] ?? 'Active'}',
                                      style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13),
                                    ),
                                  ],
                                ),
                              ),
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                decoration: BoxDecoration(
                                  color: Colors.green.withValues(alpha: 0.2),
                                  borderRadius: BorderRadius.circular(12),
                                  border: Border.all(color: Colors.green),
                                ),
                                child: const Text(
                                  'ONBOARDED',
                                  style: TextStyle(
                                    color: Colors.greenAccent,
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                            ],
                          ),
                  ),
                  const SizedBox(height: 20),

                  // Real Academic Management Summary Metrics Grid
                  Text(
                    'ACADEMIC OVERVIEW',
                    style: theme.textTheme.labelMedium?.copyWith(
                      color: AppTheme.accentCyan,
                      letterSpacing: 1.2,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),

                  if (_isLoadingSummary)
                    const Padding(
                      padding: EdgeInsets.symmetric(vertical: 24.0),
                      child: Center(child: CircularProgressIndicator()),
                    )
                  else if (_summaryError != null)
                    Card(
                      color: Colors.red.withValues(alpha: 0.2),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Text('Summary load failed: $_summaryError', style: const TextStyle(color: Colors.white)),
                      ),
                    )
                  else ...[
                    GridView.count(
                      crossAxisCount: 2,
                      crossAxisSpacing: 12,
                      mainAxisSpacing: 12,
                      childAspectRatio: 1.45,
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      children: [
                        _buildStatCard(
                          title: 'Enrolled Courses',
                          value: '${_dashboardSummary?.enrolledCoursesCount ?? 0}',
                          icon: Icons.menu_book,
                          color: Colors.blueAccent,
                          onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => CoursesScreen(authService: _authService)),
                          ),
                        ),
                        _buildStatCard(
                          title: 'Upcoming Events',
                          value: '${_dashboardSummary?.upcomingEventsCount ?? 0}',
                          icon: Icons.event,
                          color: Colors.purpleAccent,
                          onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => EventsScreen(authService: _authService)),
                          ),
                        ),
                        _buildStatCard(
                          title: 'Active Tasks',
                          value: '${_dashboardSummary?.activeTasksCount ?? 0}',
                          icon: Icons.task_alt,
                          color: Colors.orangeAccent,
                          onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => TasksScreen(authService: _authService)),
                          ),
                        ),
                        _buildStatCard(
                          title: 'Sessions This Week',
                          value: '${_dashboardSummary?.studySessionsThisWeekCount ?? 0}',
                          icon: Icons.timer,
                          color: const Color(0xFF10B981),
                          onTap: () => Navigator.push(
                            context,
                            MaterialPageRoute(builder: (_) => StudySessionsScreen(authService: _authService)),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 20),

                    // Quick Management Navigation Bar
                    Text(
                      'ACADEMIC WORKSPACE',
                      style: theme.textTheme.labelMedium?.copyWith(
                        color: AppTheme.accentCyan,
                        letterSpacing: 1.2,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),

                    Row(
                      children: [
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () => Navigator.push(
                              context,
                              MaterialPageRoute(builder: (_) => GoalsScreen(authService: _authService)),
                            ),
                            icon: const Icon(Icons.flag, size: 18),
                            label: const Text('Goals'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppTheme.surfaceColor,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: ElevatedButton.icon(
                            onPressed: () => Navigator.push(
                              context,
                              MaterialPageRoute(builder: (_) => GradesScreen(authService: _authService)),
                            ),
                            icon: const Icon(Icons.grade, size: 18),
                            label: const Text('Grades'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppTheme.surfaceColor,
                              foregroundColor: Colors.white,
                              padding: const EdgeInsets.symmetric(vertical: 14),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            ),
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 20),

                    // Recent Grades Card
                    if (_dashboardSummary != null && _dashboardSummary!.recentGrades.isNotEmpty) ...[
                      Text(
                        'RECENT GRADES',
                        style: theme.textTheme.labelMedium?.copyWith(
                          color: AppTheme.accentCyan,
                          letterSpacing: 1.2,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 10),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: AppTheme.surfaceColor.withValues(alpha: 0.8),
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: Colors.white.withValues(alpha: 0.1)),
                        ),
                        child: Column(
                          children: _dashboardSummary!.recentGrades.map((g) {
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 8.0),
                              child: Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(g.assessmentName, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                  Text(
                                    '${g.score} / ${g.maxScore} (${(g.percentage ?? 0).toStringAsFixed(1)}%)',
                                    style: const TextStyle(color: Colors.greenAccent, fontWeight: FontWeight.bold),
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
                        ),
                      ),
                      const SizedBox(height: 20),
                    ],
                  ],

                  // Test Backend Connection Widget
                  SizedBox(
                    height: 48,
                    child: OutlinedButton.icon(
                      onPressed: _isLoadingHealth ? null : _verifyBackendHealth,
                      icon: const Icon(Icons.sensors, size: 18),
                      label: const Text('Test Backend Connection'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: AppTheme.textSecondary,
                        side: BorderSide(color: Colors.white.withValues(alpha: 0.2)),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
                  ),
                  if (_healthResult != null) ...[
                    const SizedBox(height: 12),
                    Text(
                      _healthResult!,
                      textAlign: TextAlign.center,
                      style: TextStyle(color: _isSuccess ? Colors.greenAccent : Colors.orangeAccent, fontSize: 12),
                    ),
                  ],
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppTheme.surfaceColor,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Icon(icon, color: color, size: 24),
                Icon(Icons.arrow_forward_ios, color: Colors.white38, size: 14),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 24, color: color),
                ),
                const SizedBox(height: 2),
                Text(
                  title,
                  style: const TextStyle(color: AppTheme.textSecondary, fontSize: 12, fontWeight: FontWeight.w500),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
