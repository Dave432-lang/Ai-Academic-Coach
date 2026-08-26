class UserModel {
  final String id;
  final String email;
  final String accountStatus;
  final bool onboardingCompleted;
  final DateTime createdAt;

  UserModel({
    required this.id,
    required this.email,
    required this.accountStatus,
    required this.onboardingCompleted,
    required this.createdAt,
  });

  factory UserModel.fromJson(Map<String, dynamic> json) {
    return UserModel(
      id: json['id'] as String,
      email: json['email'] as String,
      accountStatus: json['account_status'] as String,
      onboardingCompleted: json['onboarding_completed'] as bool? ?? false,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}

class TokenModel {
  final String accessToken;
  final String tokenType;
  final UserModel user;

  TokenModel({
    required this.accessToken,
    required this.tokenType,
    required this.user,
  });

  factory TokenModel.fromJson(Map<String, dynamic> json) {
    return TokenModel(
      accessToken: json['access_token'] as String,
      tokenType: json['token_type'] as String? ?? 'bearer',
      user: UserModel.fromJson(json['user'] as Map<String, dynamic>),
    );
  }
}
