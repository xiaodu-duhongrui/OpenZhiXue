import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mocktail/mocktail.dart';
import 'package:go_router/go_router.dart';

import 'package:openzhixue_mobile/features/auth/presentation/pages/login_page.dart';
import 'package:openzhixue_mobile/features/auth/application/auth_controller.dart';
import 'package:openzhixue_mobile/shared/widgets/buttons/app_button.dart';
import 'package:openzhixue_mobile/shared/widgets/inputs/app_text_field.dart';

class MockAuthController extends StateNotifier<AuthState> 
    with Mock
    implements AuthController {
  MockAuthController() : super(AuthState.initial());

  Future<bool> login(String username, String password) async {
    if (username == 'testuser' && password == 'password123') {
      state = AuthState.authenticated(
        user: User(id: '1', username: 'testuser', role: 'student'),
        token: 'test-token',
      );
      return true;
    }
    return false;
  }
}

class MockGoRouter extends Mock implements GoRouter {}

void main() {
  group('LoginPage Widget Tests', () {
    testWidgets('renders login form correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const LoginPage(),
          ),
        ),
      );

      expect(find.text('欢迎回来'), findsOneWidget);
      expect(find.text('请登录您的账户'), findsOneWidget);
      expect(find.byType(AppTextField), findsNWidgets(2));
      expect(find.byType(AppButton), findsOneWidget);
    });

    testWidgets('shows validation error for empty username', 
        (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const LoginPage(),
          ),
        ),
      );

      final loginButton = find.byType(AppButton);
      await tester.tap(loginButton);
      await tester.pump();

      expect(find.text('请输入用户名'), findsOneWidget);
    });

    testWidgets('shows validation error for short password', 
        (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const LoginPage(),
          ),
        ),
      );

      final usernameField = find.widgetWithText(AppTextField, '用户名');
      await tester.enterText(usernameField, 'testuser');

      final passwordField = find.widgetWithText(AppTextField, '密码');
      await tester.enterText(passwordField, '123');

      final loginButton = find.byType(AppButton);
      await tester.tap(loginButton);
      await tester.pump();

      expect(find.text('密码长度不能少于6位'), findsOneWidget);
    });

    testWidgets('login button is disabled during loading', 
        (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: const LoginPage(),
          ),
        ),
      );

      final usernameField = find.widgetWithText(AppTextField, '用户名');
      await tester.enterText(usernameField, 'testuser');

      final passwordField = find.widgetWithText(AppTextField, '密码');
      await tester.enterText(passwordField, 'password123');

      final loginButton = find.byType(AppButton);
      await tester.tap(loginButton);
      await tester.pump();

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('navigates to forgot password page', 
        (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            routes: {
              '/': (context) => const LoginPage(),
              '/forgot-password': (context) => const Scaffold(
                body: Text('Forgot Password Page'),
              ),
            },
          ),
        ),
      );

      final forgotPasswordLink = find.text('忘记密码？');
      await tester.tap(forgotPasswordLink);
      await tester.pumpAndSettle();

      expect(find.text('Forgot Password Page'), findsOneWidget);
    });

    testWidgets('navigates to register page', (WidgetTester tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            routes: {
              '/': (context) => const LoginPage(),
              '/register': (context) => const Scaffold(
                body: Text('Register Page'),
              ),
            },
          ),
        ),
      );

      final registerLink = find.text('立即注册');
      await tester.tap(registerLink);
      await tester.pumpAndSettle();

      expect(find.text('Register Page'), findsOneWidget);
    });
  });

  group('AppTextField Widget Tests', () {
    testWidgets('renders with label and hint', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppTextField(
              label: 'Username',
              hint: 'Enter your username',
            ),
          ),
        ),
      );

      expect(find.text('Username'), findsOneWidget);
      expect(find.text('Enter your username'), findsOneWidget);
    });

    testWidgets('shows error message', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppTextField(
              label: 'Username',
              errorText: 'Username is required',
            ),
          ),
        ),
      );

      expect(find.text('Username is required'), findsOneWidget);
    });

    testWidgets('obscures text when obscureText is true', 
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppTextField(
              label: 'Password',
              obscureText: true,
            ),
          ),
        ),
      );

      final textField = tester.widget<TextField>(find.byType(TextField));
      expect(textField.obscureText, isTrue);
    });
  });

  group('AppButton Widget Tests', () {
    testWidgets('renders with text', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(text: 'Submit'),
          ),
        ),
      );

      expect(find.text('Submit'), findsOneWidget);
    });

    testWidgets('shows loading indicator when loading', 
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              text: 'Submit',
              loading: true,
            ),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('calls onPressed when tapped', (WidgetTester tester) async {
      var pressed = false;
      
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              text: 'Submit',
              onPressed: () {
                pressed = true;
              },
            ),
          ),
        ),
      );

      await tester.tap(find.byType(AppButton));
      
      expect(pressed, isTrue);
    });

    testWidgets('is disabled when onPressed is null', 
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(text: 'Submit'),
          ),
        ),
      );

      final button = tester.widget<ElevatedButton>(find.byType(ElevatedButton));
      expect(button.enabled, isFalse);
    });
  });
}
