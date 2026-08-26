import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';
import '../../models/onboarding_model.dart';
import '../../routes/app_routes.dart';
import '../../services/auth_service.dart';
import '../../services/onboarding_service.dart';

class OnboardingScreen extends StatefulWidget {
  final AuthService? authService;
  final OnboardingService? onboardingService;

  const OnboardingScreen({
    super.key,
    this.authService,
    this.onboardingService,
  });

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  late final AuthService _authService;
  late final OnboardingService _onboardingService;

  int _currentStep = 0; // 0: Profile, 1: University, 2: Academic Info, 3: Courses, 4: Review
  bool _isLoading = false;
  String? _errorMessage;

  // Step 1 Controllers
  final _fullNameController = TextEditingController();
  final _countryController = TextEditingController(text: 'Ghana');
  String _timezone = 'Africa/Accra';

  // Step 2 University Controllers
  final _searchUniversityController = TextEditingController();
  List<UniversityModel> _searchedUniversities = [];
  UniversityModel? _selectedUniversity;
  final _newUnivNameController = TextEditingController();
  final _newUnivCountryController = TextEditingController(text: 'Ghana');
  bool _isCreatingUniv = false;

  // Step 3 Academic Controllers
  final _programController = TextEditingController(text: 'Computer Science');
  String _level = 'Undergraduate Level 300';
  final _academicYearController = TextEditingController(text: '2026/2027');
  String _semester = 'Semester 1';

  // Step 4 Courses Controllers
  final _courseCodeController = TextEditingController();
  final _courseNameController = TextEditingController();
  final _creditHoursController = TextEditingController(text: '3');
  final List<CourseEnrollmentModel> _addedCourses = [];

  @override
  void initState() {
    super.initState();
    _authService = widget.authService ?? AuthService();
    _onboardingService = widget.onboardingService ?? OnboardingService(authService: _authService);
    _fetchExistingStatus();
  }

  @override
  void dispose() {
    _fullNameController.dispose();
    _countryController.dispose();
    _searchUniversityController.dispose();
    _newUnivNameController.dispose();
    _newUnivCountryController.dispose();
    _programController.dispose();
    _academicYearController.dispose();
    _courseCodeController.dispose();
    _courseNameController.dispose();
    _creditHoursController.dispose();
    super.dispose();
  }

  Future<void> _fetchExistingStatus() async {
    try {
      final status = await _onboardingService.getOnboardingStatus();
      if (status.onboardingCompleted && mounted) {
        Navigator.pushNamedAndRemoveUntil(context, AppRoutes.home, (route) => false);
      }
    } catch (_) {}
  }

  // --- Step Actions ---

  Future<void> _saveProfileStep() async {
    if (_fullNameController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter your full name');
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _onboardingService.updateProfile(
        fullName: _fullNameController.text.trim(),
        country: _countryController.text.trim(),
        timezone: _timezone,
      );
      setState(() {
        _isLoading = false;
        _currentStep = 1; // Move to University Step
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    }
  }

  Future<void> _searchUniversities(String query) async {
    try {
      final results = await _onboardingService.searchUniversities(search: query);
      setState(() {
        _searchedUniversities = results;
      });
    } catch (_) {}
  }

  Future<void> _handleCreateUniversity() async {
    if (_newUnivNameController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter university name');
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final univ = await _onboardingService.createUniversity(
        name: _newUnivNameController.text.trim(),
        country: _newUnivCountryController.text.trim(),
        timezone: _timezone,
      );
      setState(() {
        _selectedUniversity = univ;
        _isCreatingUniv = false;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    }
  }

  Future<void> _saveUniversityStep() async {
    if (_selectedUniversity == null) {
      setState(() => _errorMessage = 'Please select or create your university');
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _onboardingService.updateProfile(
        fullName: _fullNameController.text.trim(),
        country: _countryController.text.trim(),
        timezone: _timezone,
        universityId: _selectedUniversity!.id,
      );
      setState(() {
        _isLoading = false;
        _currentStep = 2; // Move to Academic Info Step
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    }
  }

  Future<void> _saveAcademicInfoStep() async {
    if (_programController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter your academic program');
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _onboardingService.updateProfile(
        fullName: _fullNameController.text.trim(),
        country: _countryController.text.trim(),
        timezone: _timezone,
        universityId: _selectedUniversity?.id,
        program: _programController.text.trim(),
        level: _level,
        academicYear: _academicYearController.text.trim(),
        semester: _semester,
      );
      setState(() {
        _isLoading = false;
        _currentStep = 3; // Move to Courses Step
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    }
  }

  Future<void> _handleAddCourse() async {
    if (_courseCodeController.text.trim().isEmpty || _courseNameController.text.trim().isEmpty) {
      setState(() => _errorMessage = 'Please enter both course code and course name');
      return;
    }
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final enrollment = await _onboardingService.addCourseAndEnroll(
        courseCode: _courseCodeController.text.trim().toUpperCase(),
        courseName: _courseNameController.text.trim(),
        creditHours: int.tryParse(_creditHoursController.text) ?? 3,
        academicYear: _academicYearController.text.trim(),
        semester: _semester,
      );
      setState(() {
        _addedCourses.add(enrollment);
        _courseCodeController.clear();
        _courseNameController.clear();
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    }
  }

  Future<void> _saveCoursesStep() async {
    if (_addedCourses.isEmpty) {
      setState(() => _errorMessage = 'At least one active course enrollment is required to complete onboarding');
      return;
    }
    setState(() {
      _errorMessage = null;
      _currentStep = 4; // Move to Review Step
    });
  }

  Future<void> _handleCompleteOnboarding() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await _onboardingService.completeOnboarding();
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Academic Onboarding Completed! Welcome to your Dashboard.'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pushNamedAndRemoveUntil(context, AppRoutes.home, (route) => false);
    } catch (e) {
      setState(() {
        _isLoading = false;
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    }
  }

  // --- Step Builders ---

  Widget _buildStep1Profile() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Step 1: Student Profile', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        const Text('Tell us your name and region to personalize your study assistant.', style: TextStyle(color: AppTheme.textSecondary)),
        const SizedBox(height: 24),
        TextField(
          controller: _fullNameController,
          decoration: InputDecoration(
            labelText: 'Full Name',
            hintText: 'e.g. Ama Mensah',
            prefixIcon: const Icon(Icons.person_outline),
            filled: true,
            fillColor: AppTheme.surfaceColor,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _countryController,
          decoration: InputDecoration(
            labelText: 'Country',
            prefixIcon: const Icon(Icons.public_outlined),
            filled: true,
            fillColor: AppTheme.surfaceColor,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 16),
        DropdownButtonFormField<String>(
          initialValue: _timezone,
          decoration: InputDecoration(
            labelText: 'Timezone',
            prefixIcon: const Icon(Icons.access_time),
            filled: true,
            fillColor: AppTheme.surfaceColor,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
          items: const [
            DropdownMenuItem(value: 'Africa/Accra', child: Text('Africa/Accra (GMT+0)')),
            DropdownMenuItem(value: 'UTC', child: Text('UTC')),
            DropdownMenuItem(value: 'America/New_York', child: Text('America/New_York (EST)')),
            DropdownMenuItem(value: 'Europe/London', child: Text('Europe/London (BST)')),
          ],
          onChanged: (val) {
            if (val != null) setState(() => _timezone = val);
          },
        ),
        const SizedBox(height: 28),
        ElevatedButton(
          onPressed: _isLoading ? null : _saveProfileStep,
          style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryColor, padding: const EdgeInsets.symmetric(vertical: 16)),
          child: _isLoading
              ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
              : const Text('Continue to University', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }

  Widget _buildStep2University() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Step 2: Select University', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        const Text('Search and select your university, or add a new institution.', style: TextStyle(color: AppTheme.textSecondary)),
        const SizedBox(height: 20),
        if (_selectedUniversity != null) ...[
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.primaryColor.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: AppTheme.primaryColor),
            ),
            child: Row(
              children: [
                const Icon(Icons.account_balance, color: AppTheme.primaryColor),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(_selectedUniversity!.name, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      Text(_selectedUniversity!.country, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13)),
                    ],
                  ),
                ),
                TextButton(
                  onPressed: () => setState(() => _selectedUniversity = null),
                  child: const Text('Change'),
                )
              ],
            ),
          ),
          const SizedBox(height: 24),
        ] else if (_isCreatingUniv) ...[
          const Text('Add New University', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          const SizedBox(height: 12),
          TextField(
            controller: _newUnivNameController,
            decoration: InputDecoration(
              labelText: 'University Name',
              hintText: 'e.g. Ashesi University',
              filled: true,
              fillColor: AppTheme.surfaceColor,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _newUnivCountryController,
            decoration: InputDecoration(
              labelText: 'Country',
              filled: true,
              fillColor: AppTheme.surfaceColor,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => setState(() => _isCreatingUniv = false),
                  child: const Text('Cancel'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton(
                  onPressed: _isLoading ? null : _handleCreateUniversity,
                  style: ElevatedButton.styleFrom(backgroundColor: AppTheme.secondaryColor),
                  child: const Text('Save Institution', style: TextStyle(color: Colors.white)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
        ] else ...[
          TextField(
            controller: _searchUniversityController,
            onChanged: _searchUniversities,
            decoration: InputDecoration(
              labelText: 'Search University',
              hintText: 'Type university name...',
              prefixIcon: const Icon(Icons.search),
              filled: true,
              fillColor: AppTheme.surfaceColor,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
            ),
          ),
          const SizedBox(height: 12),
          if (_searchedUniversities.isNotEmpty)
            Container(
              constraints: const BoxConstraints(maxHeight: 200),
              decoration: BoxDecoration(color: AppTheme.surfaceColor, borderRadius: BorderRadius.circular(12)),
              child: ListView.builder(
                shrinkWrap: true,
                itemCount: _searchedUniversities.length,
                itemBuilder: (context, index) {
                  final univ = _searchedUniversities[index];
                  return ListTile(
                    title: Text(univ.name),
                    subtitle: Text(univ.country),
                    onTap: () {
                      setState(() {
                        _selectedUniversity = univ;
                      });
                    },
                  );
                },
              ),
            ),
          const SizedBox(height: 12),
          TextButton.icon(
            onPressed: () => setState(() => _isCreatingUniv = true),
            icon: const Icon(Icons.add_circle_outline),
            label: const Text('Can\'t find your university? Add it here'),
          ),
          const SizedBox(height: 24),
        ],
        ElevatedButton(
          onPressed: (_isLoading || _selectedUniversity == null) ? null : _saveUniversityStep,
          style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryColor, padding: const EdgeInsets.symmetric(vertical: 16)),
          child: _isLoading
              ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
              : const Text('Continue to Academic Info', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }

  Widget _buildStep3AcademicInfo() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Step 3: Academic Details', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        const Text('Provide your major, current level, and active term.', style: TextStyle(color: AppTheme.textSecondary)),
        const SizedBox(height: 24),
        TextField(
          controller: _programController,
          decoration: InputDecoration(
            labelText: 'Program / Major',
            hintText: 'e.g. Computer Science',
            prefixIcon: const Icon(Icons.menu_book_outlined),
            filled: true,
            fillColor: AppTheme.surfaceColor,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 16),
        DropdownButtonFormField<String>(
          initialValue: _level,
          decoration: InputDecoration(
            labelText: 'Academic Level',
            prefixIcon: const Icon(Icons.stars_outlined),
            filled: true,
            fillColor: AppTheme.surfaceColor,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
          items: const [
            DropdownMenuItem(value: 'Undergraduate Level 100', child: Text('Undergraduate Level 100')),
            DropdownMenuItem(value: 'Undergraduate Level 200', child: Text('Undergraduate Level 200')),
            DropdownMenuItem(value: 'Undergraduate Level 300', child: Text('Undergraduate Level 300')),
            DropdownMenuItem(value: 'Undergraduate Level 400', child: Text('Undergraduate Level 400')),
            DropdownMenuItem(value: 'Postgraduate Master\'s', child: Text('Postgraduate Master\'s')),
            DropdownMenuItem(value: 'Postgraduate PhD', child: Text('Postgraduate PhD')),
          ],
          onChanged: (val) {
            if (val != null) setState(() => _level = val);
          },
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _academicYearController,
          decoration: InputDecoration(
            labelText: 'Academic Year',
            hintText: '2026/2027',
            prefixIcon: const Icon(Icons.calendar_today_outlined),
            filled: true,
            fillColor: AppTheme.surfaceColor,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
        ),
        const SizedBox(height: 16),
        DropdownButtonFormField<String>(
          initialValue: _semester,
          decoration: InputDecoration(
            labelText: 'Semester / Term',
            prefixIcon: const Icon(Icons.timeline_outlined),
            filled: true,
            fillColor: AppTheme.surfaceColor,
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
          ),
          items: const [
            DropdownMenuItem(value: 'Semester 1', child: Text('Semester 1')),
            DropdownMenuItem(value: 'Semester 2', child: Text('Semester 2')),
            DropdownMenuItem(value: 'Trimester 1', child: Text('Trimester 1')),
            DropdownMenuItem(value: 'Summer Term', child: Text('Summer Term')),
          ],
          onChanged: (val) {
            if (val != null) setState(() => _semester = val);
          },
        ),
        const SizedBox(height: 28),
        ElevatedButton(
          onPressed: _isLoading ? null : _saveAcademicInfoStep,
          style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryColor, padding: const EdgeInsets.symmetric(vertical: 16)),
          child: _isLoading
              ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
              : const Text('Continue to Courses', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }

  Widget _buildStep4Courses() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Step 4: Active Courses', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        const Text('Add at least 1 active course for your current term.', style: TextStyle(color: AppTheme.textSecondary)),
        const SizedBox(height: 20),
        Row(
          children: [
            Expanded(
              flex: 2,
              child: TextField(
                controller: _courseCodeController,
                decoration: InputDecoration(
                  labelText: 'Course Code',
                  hintText: 'CS101',
                  filled: true,
                  fillColor: AppTheme.surfaceColor,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              flex: 3,
              child: TextField(
                controller: _courseNameController,
                decoration: InputDecoration(
                  labelText: 'Course Name',
                  hintText: 'Intro to CS',
                  filled: true,
                  fillColor: AppTheme.surfaceColor,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12), borderSide: BorderSide.none),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        ElevatedButton.icon(
          onPressed: _isLoading ? null : _handleAddCourse,
          icon: const Icon(Icons.add, color: Colors.white),
          label: const Text('Add Course', style: TextStyle(color: Colors.white)),
          style: ElevatedButton.styleFrom(backgroundColor: AppTheme.secondaryColor),
        ),
        const SizedBox(height: 20),
        const Text('Enrolled Courses:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
        const SizedBox(height: 8),
        if (_addedCourses.isEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: AppTheme.surfaceColor, borderRadius: BorderRadius.circular(12)),
            child: const Center(child: Text('No courses added yet. Please add at least one course.', style: TextStyle(color: AppTheme.textSecondary))),
          )
        else
          ListView.builder(
            shrinkWrap: true,
            itemCount: _addedCourses.length,
            itemBuilder: (context, index) {
              final course = _addedCourses[index];
              return Card(
                child: ListTile(
                  leading: const CircleAvatar(backgroundColor: AppTheme.primaryColor, child: Icon(Icons.book, color: Colors.white, size: 20)),
                  title: Text('${course.courseCode}: ${course.courseName}', style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text('${course.academicYear} | ${course.semester}'),
                ),
              );
            },
          ),
        const SizedBox(height: 28),
        ElevatedButton(
          onPressed: (_isLoading || _addedCourses.isEmpty) ? null : _saveCoursesStep,
          style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primaryColor, padding: const EdgeInsets.symmetric(vertical: 16)),
          child: const Text('Continue to Final Review', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }

  Widget _buildStep5Review() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Step 5: Review & Complete', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        const Text('Review your academic profile setup before completing onboarding.', style: TextStyle(color: AppTheme.textSecondary)),
        const SizedBox(height: 20),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _buildReviewRow('Student Name', _fullNameController.text),
                _buildReviewRow('Country', _countryController.text),
                _buildReviewRow('University', _selectedUniversity?.name ?? 'Not selected'),
                _buildReviewRow('Program', _programController.text),
                _buildReviewRow('Level', _level),
                _buildReviewRow('Academic Term', '${_academicYearController.text} ($_semester)'),
                _buildReviewRow('Active Courses', '${_addedCourses.length} course(s) enrolled'),
              ],
            ),
          ),
        ),
        const SizedBox(height: 28),
        ElevatedButton(
          onPressed: _isLoading ? null : _handleCompleteOnboarding,
          style: ElevatedButton.styleFrom(backgroundColor: Colors.green, padding: const EdgeInsets.symmetric(vertical: 16)),
          child: _isLoading
              ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
              : const Text('Complete Onboarding', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
        ),
      ],
    );
  }

  Widget _buildReviewRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppTheme.textSecondary, fontSize: 14)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Onboarding (Step ${_currentStep + 1} of 5)'),
      ),
      body: SafeArea(
        child: Column(
          children: [
            // Progress Indicator
            LinearProgressIndicator(
              value: (_currentStep + 1) / 5.0,
              backgroundColor: AppTheme.surfaceColor,
              color: AppTheme.primaryColor,
            ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (_errorMessage != null) ...[
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.red.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: Colors.red.withValues(alpha: 0.5)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.error_outline, color: Colors.redAccent),
                            const SizedBox(width: 10),
                            Expanded(child: Text(_errorMessage!, style: const TextStyle(color: Colors.redAccent, fontSize: 14))),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                    ],
                    if (_currentStep == 0) _buildStep1Profile(),
                    if (_currentStep == 1) _buildStep2University(),
                    if (_currentStep == 2) _buildStep3AcademicInfo(),
                    if (_currentStep == 3) _buildStep4Courses(),
                    if (_currentStep == 4) _buildStep5Review(),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
