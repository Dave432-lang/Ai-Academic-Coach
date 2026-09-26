import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../../models/academic_models.dart';
import '../../../services/academic_service.dart';
import '../../../services/auth_service.dart';

class MaterialsScreen extends StatefulWidget {
  final AcademicService? academicService;

  const MaterialsScreen({super.key, this.academicService});

  @override
  State<MaterialsScreen> createState() => _MaterialsScreenState();
}

class _MaterialsScreenState extends State<MaterialsScreen> {
  late final AcademicService _academicService;
  bool _isLoading = true;
  String? _errorMessage;

  List<CourseMaterialModel> _materials = [];
  List<AcademicCourseEnrollmentModel> _courses = [];
  String? _selectedCourseFilter;

  @override
  void initState() {
    super.initState();
    _academicService = widget.academicService ?? AcademicService(authService: AuthService());
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final courses = await _academicService.fetchCourses();
      final materials = await _academicService.fetchMaterials(courseId: _selectedCourseFilter);

      if (!mounted) return;
      setState(() {
        _courses = courses;
        _materials = materials;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      final errStr = e.toString();
      if (errStr.contains('Not authenticated') || errStr.contains('Could not validate credentials')) {
        _academicService.authService.handleSessionExpired(context);
        return;
      }
      setState(() {
        _errorMessage = errStr.replaceAll('Exception: ', '');
        _isLoading = false;
      });
    }
  }

  String _formatFileSize(int? bytes) {
    if (bytes == null || bytes == 0) return '0 B';
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(1)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(1)} MB';
  }

  IconData _getFileIcon(String fileType, String fileName) {
    final lowerName = fileName.toLowerCase();
    final lowerType = fileType.toLowerCase();

    if (lowerName.endsWith('.pdf') || lowerType.contains('pdf')) {
      return Icons.picture_as_pdf;
    } else if (lowerName.endsWith('.docx') || lowerName.endsWith('.doc') || lowerType.contains('word')) {
      return Icons.description;
    } else if (lowerName.endsWith('.pptx') || lowerName.endsWith('.ppt') || lowerType.contains('presentation')) {
      return Icons.slideshow;
    }
    return Icons.insert_drive_file;
  }

  Color _getFileIconColor(String fileType, String fileName) {
    final lowerName = fileName.toLowerCase();
    if (lowerName.endsWith('.pdf')) return Colors.red;
    if (lowerName.endsWith('.docx') || lowerName.endsWith('.doc')) return Colors.blue;
    if (lowerName.endsWith('.pptx') || lowerName.endsWith('.ppt')) return Colors.orange;
    return Colors.teal;
  }

  Future<void> _downloadMaterial(CourseMaterialModel material) async {
    try {
      final downloadUrl = await _academicService.getMaterialDownloadUrl(material.id);
      final uri = Uri.parse(downloadUrl);

      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        await launchUrl(uri);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not open download link: $e')),
        );
      }
    }
  }

  Future<void> _confirmDelete(CourseMaterialModel material) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Course Material'),
        content: Text('Are you sure you want to delete "${material.fileName}"? This action cannot be undone.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
            onPressed: () => Navigator.of(context).pop(true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await _academicService.deleteMaterial(material.id);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Material deleted successfully')),
          );
          _loadData();
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Failed to delete material: $e'), backgroundColor: Colors.red),
          );
        }
      }
    }
  }

  Future<void> _showUploadDialog() async {
    if (_courses.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('You must be enrolled in at least one course to upload materials.')),
      );
      return;
    }

    String selectedCourseId = _selectedCourseFilter ?? _courses.first.courseId;
    final titleController = TextEditingController();
    PlatformFile? pickedFile;
    bool isUploading = false;
    String? uploadError;

    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setBottomSheetState) {
            return Padding(
              padding: EdgeInsets.only(
                bottom: MediaQuery.of(context).viewInsets.bottom + 16,
                top: 24,
                left: 16,
                right: 16,
              ),
              child: SingleChildScrollView(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    Text(
                      'Upload Course Material',
                      style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 16),
                    if (uploadError != null)
                      Container(
                        padding: const EdgeInsets.all(8),
                        margin: const EdgeInsets.only(bottom: 12),
                        decoration: BoxDecoration(
                          color: Colors.red.shade50,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: Colors.red.shade200),
                        ),
                        child: Text(
                          uploadError!,
                          style: TextStyle(color: Colors.red.shade800, fontSize: 13),
                        ),
                      ),

                    // Course Dropdown
                    DropdownButtonFormField<String>(
                      value: selectedCourseId,
                      decoration: const InputDecoration(
                        labelText: 'Course',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.class_),
                      ),
                      items: _courses.map((enrollment) {
                        return DropdownMenuItem<String>(
                          value: enrollment.courseId,
                          child: Text('${enrollment.course.courseCode} - ${enrollment.course.courseName}'),
                        );
                      }).toList(),
                      onChanged: (val) {
                        if (val != null) {
                          setBottomSheetState(() => selectedCourseId = val);
                        }
                      },
                    ),
                    const SizedBox(height: 12),

                    // Custom Title Field
                    TextField(
                      controller: titleController,
                      decoration: const InputDecoration(
                        labelText: 'Document Title (Optional)',
                        hintText: 'e.g. Week 1 Lecture Notes',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.title),
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Pick File Button & File Info Display
                    OutlinedButton.icon(
                      onPressed: isUploading
                          ? null
                          : () async {
                              final result = await FilePicker.platform.pickFiles(
                                type: FileType.custom,
                                allowedExtensions: ['pdf', 'pptx', 'docx', 'doc', 'ppt'],
                                withData: true,
                              );
                              if (result != null && result.files.isNotEmpty) {
                                setBottomSheetState(() {
                                  pickedFile = result.files.first;
                                  uploadError = null;
                                });
                              }
                            },
                      icon: const Icon(Icons.attach_file),
                      label: Text(pickedFile != null ? 'Change Selected File' : 'Select Document File (PDF, DOCX, PPTX)'),
                    ),
                    if (pickedFile != null)
                      Container(
                        margin: const EdgeInsets.only(top: 8),
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          children: [
                            Icon(_getFileIcon('', pickedFile!.name), color: _getFileIconColor('', pickedFile!.name)),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    pickedFile!.name,
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                    style: const TextStyle(fontWeight: FontWeight.bold),
                                  ),
                                  Text(_formatFileSize(pickedFile!.size), style: TextStyle(color: Colors.grey.shade700, fontSize: 12)),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                    const SizedBox(height: 20),

                    // Upload Button
                    ElevatedButton(
                      onPressed: (pickedFile == null || isUploading)
                          ? null
                          : () async {
                              setBottomSheetState(() {
                                isUploading = true;
                                uploadError = null;
                              });

                              try {
                                final bytes = pickedFile!.bytes;
                                if (bytes == null || bytes.isEmpty) {
                                  throw Exception('Could not read file contents');
                                }

                                await _academicService.uploadMaterial(
                                  courseId: selectedCourseId,
                                  fileBytes: bytes,
                                  fileName: pickedFile!.name,
                                  title: titleController.text.trim(),
                                );

                                if (mounted) {
                                  Navigator.of(context).pop();
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Course material uploaded successfully!')),
                                  );
                                  _loadData();
                                }
                              } catch (e) {
                                setBottomSheetState(() {
                                  isUploading = false;
                                  uploadError = e.toString().replaceAll('Exception: ', '');
                                });
                              }
                            },
                      child: isUploading
                          ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                            )
                          : const Text('Upload Document'),
                    ),
                    const SizedBox(height: 12),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Course Materials'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadData,
            tooltip: 'Refresh',
          ),
        ],
      ),
      body: Column(
        children: [
          // Filter Bar
          if (_courses.isNotEmpty)
            Padding(
              padding: const EdgeInsets.all(12.0),
              child: DropdownButtonFormField<String?>(
                value: _selectedCourseFilter,
                decoration: const InputDecoration(
                  labelText: 'Filter by Course',
                  border: OutlineInputBorder(),
                  contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                ),
                items: [
                  const DropdownMenuItem<String?>(
                    value: null,
                    child: Text('All Enrolled Courses'),
                  ),
                  ..._courses.map((enrollment) {
                    return DropdownMenuItem<String?>(
                      value: enrollment.courseId,
                      child: Text('${enrollment.course.courseCode} - ${enrollment.course.courseName}'),
                    );
                  }),
                ],
                onChanged: (val) {
                  setState(() {
                    _selectedCourseFilter = val;
                  });
                  _loadData();
                },
              ),
            ),

          // Main Content
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _errorMessage != null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
                            const SizedBox(height: 12),
                            ElevatedButton(onPressed: _loadData, child: const Text('Retry')),
                          ],
                        ),
                      )
                    : _materials.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.folder_open, size: 64, color: Colors.grey.shade400),
                                const SizedBox(height: 16),
                                Text(
                                  'No course materials uploaded yet.',
                                  style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.grey.shade600),
                                ),
                                const SizedBox(height: 8),
                                const Text('Tap "+" below to upload slides, notes, or PDFs.'),
                              ],
                            ),
                          )
                        : ListView.builder(
                            itemCount: _materials.length,
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            itemBuilder: (context, index) {
                              final mat = _materials[index];
                              final formattedDate = DateFormat('MMM d, yyyy • h:mm a').format(mat.createdAt.toLocal());
                              final icon = _getFileIcon(mat.fileType, mat.fileName);
                              final iconColor = _getFileIconColor(mat.fileType, mat.fileName);

                              return Card(
                                margin: const EdgeInsets.only(bottom: 10),
                                elevation: 2,
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                                child: ListTile(
                                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                  leading: CircleAvatar(
                                    backgroundColor: iconColor.withOpacity(0.1),
                                    child: Icon(icon, color: iconColor),
                                  ),
                                  title: Text(
                                    mat.fileName,
                                    style: const TextStyle(fontWeight: FontWeight.bold),
                                    maxLines: 1,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  subtitle: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      const SizedBox(height: 4),
                                      Text(
                                        '${mat.courseCode ?? 'Course'} • ${_formatFileSize(mat.fileSize)}',
                                        style: TextStyle(color: Colors.grey.shade800, fontSize: 13),
                                      ),
                                      const SizedBox(height: 2),
                                      Text(
                                        formattedDate,
                                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12),
                                      ),
                                      const SizedBox(height: 6),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: Colors.amber.shade100,
                                          borderRadius: BorderRadius.circular(12),
                                        ),
                                        child: Text(
                                          'Status: ${mat.processingStatus.toUpperCase()}',
                                          style: TextStyle(color: Colors.amber.shade900, fontSize: 10, fontWeight: FontWeight.bold),
                                        ),
                                      ),
                                    ],
                                  ),
                                  trailing: Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      IconButton(
                                        icon: const Icon(Icons.download_rounded, color: Colors.blue),
                                        tooltip: 'Download / View',
                                        onPressed: () => _downloadMaterial(mat),
                                      ),
                                      IconButton(
                                        icon: const Icon(Icons.delete_outline, color: Colors.red),
                                        tooltip: 'Delete Material',
                                        onPressed: () => _confirmDelete(mat),
                                      ),
                                    ],
                                  ),
                                ),
                              );
                            },
                          ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _showUploadDialog,
        icon: const Icon(Icons.upload_file),
        label: const Text('Upload Material'),
      ),
    );
  }
}
