import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;
import '../core/config/api_config.dart';
import '../models/user_model.dart';
import '../routes/app_routes.dart';

class AuthService {
  final http.Client client;
  final FlutterSecureStorage storage;
  static const String _tokenStorageKey = 'jwt_access_token';
  static String? _cachedToken;

  AuthService({
    http.Client? client,
    FlutterSecureStorage? storage,
  })  : client = client ?? http.Client(),
        storage = storage ?? const FlutterSecureStorage();

  /// Gets the currently active JWT token, reading from secure storage if cached value is null
  Future<String?> getAuthToken() async {
    _cachedToken ??= await storage.read(key: _tokenStorageKey);
    return _cachedToken;
  }

  /// Sets or clears active auth token in encrypted secure storage
  Future<void> setAuthToken(String? token) async {
    _cachedToken = token;
    if (token != null && token.isNotEmpty) {
      await storage.write(key: _tokenStorageKey, value: token);
    } else {
      await storage.delete(key: _tokenStorageKey);
    }
  }

  /// Returns authorization headers map (async to fetch token securely)
  Future<Map<String, String>> getAuthHeaders() async {
    final token = await getAuthToken();
    final headers = <String, String>{
      'Content-Type': 'application/json',
    };
    if (token != null && token.isNotEmpty) {
      headers['Authorization'] = 'Bearer $token';
    }
    return headers;
  }

  /// Student Account Registration (POST /api/v1/auth/signup)
  Future<Map<String, dynamic>> signup({
    required String email,
    required String password,
  }) async {
    final uri = Uri.parse(ApiConfig.authSignupEndpoint);
    try {
      final response = await client.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email.trim(),
          'password': password,
        }),
      );

      final Map<String, dynamic> body = jsonDecode(response.body);

      if (response.statusCode == 201) {
        final tokenModel = TokenModel.fromJson(body);
        await setAuthToken(tokenModel.accessToken);
        return {
          'success': true,
          'statusCode': response.statusCode,
          'token': tokenModel,
        };
      } else {
        return {
          'success': false,
          'statusCode': response.statusCode,
          'error': body['detail'] ?? 'Registration failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'statusCode': 0,
        'error': 'Network error during signup: $e',
      };
    }
  }

  /// Student Account Login (POST /api/v1/auth/login)
  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final uri = Uri.parse(ApiConfig.authLoginEndpoint);
    try {
      final response = await client.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email.trim(),
          'password': password,
        }),
      );

      final Map<String, dynamic> body = jsonDecode(response.body);

      if (response.statusCode == 200) {
        final tokenModel = TokenModel.fromJson(body);
        await setAuthToken(tokenModel.accessToken);
        return {
          'success': true,
          'statusCode': response.statusCode,
          'token': tokenModel,
        };
      } else {
        return {
          'success': false,
          'statusCode': response.statusCode,
          'error': body['detail'] ?? 'Login failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'statusCode': 0,
        'error': 'Network error during login: $e',
      };
    }
  }

  /// Retrieve Current Authenticated User Details (GET /api/v1/auth/me)
  Future<Map<String, dynamic>> getMe() async {
    final token = await getAuthToken();
    if (token == null || token.isEmpty) {
      return {
        'success': false,
        'statusCode': 401,
        'error': 'No auth token available',
      };
    }

    final uri = Uri.parse(ApiConfig.authMeEndpoint);
    try {
      final headers = await getAuthHeaders();
      final response = await client.get(
        uri,
        headers: headers,
      );

      final Map<String, dynamic> body = jsonDecode(response.body);

      if (response.statusCode == 200) {
        return {
          'success': true,
          'statusCode': response.statusCode,
          'user': body,
        };
      } else {
        if (response.statusCode == 401 || response.statusCode == 403) {
          await setAuthToken(null); // Clear token on invalid/expired/suspended session
        }
        return {
          'success': false,
          'statusCode': response.statusCode,
          'error': body['detail'] ?? 'Session verification failed',
        };
      }
    } catch (e) {
      return {
        'success': false,
        'statusCode': 0,
        'error': 'Network error checking user profile: $e',
      };
    }
  }

  /// Log out current user and clear token from secure storage
  Future<void> logout() async {
    await setAuthToken(null);
  }

  /// Central session expiration handler when any request returns 401 Unauthorized
  Future<void> handleSessionExpired(
    BuildContext context, {
    String message = 'Your session has expired — please log in again.',
  }) async {
    await logout();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(message),
            backgroundColor: Colors.redAccent,
            behavior: SnackBarBehavior.floating,
          ),
        );
        Navigator.pushNamedAndRemoveUntil(context, AppRoutes.login, (route) => false);
      }
    });
  }
}
