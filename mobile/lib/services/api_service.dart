import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/config/api_config.dart';

class ApiService {
  final http.Client client;

  ApiService({http.Client? client}) : client = client ?? http.Client();

  /// Tests connectivity to backend GET /health endpoint.
  Future<Map<String, dynamic>> checkHealth() async {
    final uri = Uri.parse(ApiConfig.healthEndpoint);
    try {
      final response = await client.get(uri).timeout(
        const Duration(seconds: 5),
      );

      if (response.statusCode == 200) {
        final Map<String, dynamic> data = jsonDecode(response.body);
        return {
          "success": true,
          "statusCode": response.statusCode,
          "data": data,
        };
      } else {
        return {
          "success": false,
          "statusCode": response.statusCode,
          "error": "Server returned status ${response.statusCode}",
        };
      }
    } catch (e) {
      return {
        "success": false,
        "statusCode": 0,
        "error": "Failed to connect to backend at ${ApiConfig.baseUrl}: $e",
      };
    }
  }
}
