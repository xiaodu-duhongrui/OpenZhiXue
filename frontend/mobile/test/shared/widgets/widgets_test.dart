import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:openzhixue_mobile/shared/widgets/buttons/app_button.dart';
import 'package:openzhixue_mobile/shared/widgets/buttons/app_icon_button.dart';
import 'package:openzhixue_mobile/shared/widgets/cards/app_card.dart';
import 'package:openzhixue_mobile/shared/widgets/cards/app_list_tile.dart';
import 'package:openzhixue_mobile/shared/widgets/inputs/app_text_field.dart';
import 'package:openzhixue_mobile/shared/widgets/common/app_avatar.dart';
import 'package:openzhixue_mobile/shared/widgets/feedback/app_feedback.dart';

void main() {
  group('AppButton Tests', () {
    testWidgets('renders text correctly', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(text: 'Test Button'),
          ),
        ),
      );

      expect(find.text('Test Button'), findsOneWidget);
    });

    testWidgets('handles press events', (WidgetTester tester) async {
      int pressCount = 0;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              text: 'Press Me',
              onPressed: () {
                pressCount++;
              },
            ),
          ),
        ),
      );

      await tester.tap(find.byType(AppButton));
      expect(pressCount, equals(1));
    });

    testWidgets('shows loading state', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppButton(
              text: 'Loading Button',
              loading: true,
            ),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('applies different variants', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Column(
              children: [
                AppButton(text: 'Primary', variant: AppButtonVariant.primary),
                AppButton(text: 'Secondary', variant: AppButtonVariant.secondary),
                AppButton(text: 'Outline', variant: AppButtonVariant.outline),
              ],
            ),
          ),
        ),
      );

      expect(find.text('Primary'), findsOneWidget);
      expect(find.text('Secondary'), findsOneWidget);
      expect(find.text('Outline'), findsOneWidget);
    });
  });

  group('AppCard Tests', () {
    testWidgets('renders child content', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppCard(
              child: Text('Card Content'),
            ),
          ),
        ),
      );

      expect(find.text('Card Content'), findsOneWidget);
    });

    testWidgets('handles tap events', (WidgetTester tester) async {
      bool tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppCard(
              onTap: () {
                tapped = true;
              },
              child: Text('Tappable Card'),
            ),
          ),
        ),
      );

      await tester.tap(find.byType(AppCard));
      expect(tapped, isTrue);
    });
  });

  group('AppTextField Tests', () {
    testWidgets('renders with label', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppTextField(
              label: 'Email',
              hint: 'Enter your email',
            ),
          ),
        ),
      );

      expect(find.text('Email'), findsOneWidget);
      expect(find.text('Enter your email'), findsOneWidget);
    });

    testWidgets('validates input', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppTextField(
              label: 'Email',
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'Email is required';
                }
                if (!value.contains('@')) {
                  return 'Invalid email format';
                }
                return null;
              },
            ),
          ),
        ),
      );

      final textField = find.byType(TextField);
      await tester.enterText(textField, 'invalid-email');
      
      final input = tester.widget<TextField>(textField);
      expect(input.controller?.text, equals('invalid-email'));
    });

    testWidgets('obscures password text', (WidgetTester tester) async {
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

  group('AppAvatar Tests', () {
    testWidgets('renders with image URL', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppAvatar(
              imageUrl: 'https://example.com/avatar.jpg',
              radius: 24,
            ),
          ),
        ),
      );

      expect(find.byType(CircleAvatar), findsOneWidget);
    });

    testWidgets('renders with initials when no image', 
        (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppAvatar(
              name: 'John Doe',
              radius: 24,
            ),
          ),
        ),
      );

      expect(find.text('JD'), findsOneWidget);
    });
  });

  group('AppListTile Tests', () {
    testWidgets('renders title and subtitle', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppListTile(
              title: 'List Item Title',
              subtitle: 'List Item Subtitle',
            ),
          ),
        ),
      );

      expect(find.text('List Item Title'), findsOneWidget);
      expect(find.text('List Item Subtitle'), findsOneWidget);
    });

    testWidgets('handles tap events', (WidgetTester tester) async {
      bool tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppListTile(
              title: 'Tappable Item',
              onTap: () {
                tapped = true;
              },
            ),
          ),
        ),
      );

      await tester.tap(find.byType(AppListTile));
      expect(tapped, isTrue);
    });

    testWidgets('shows trailing widget', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppListTile(
              title: 'Item with Trailing',
              trailing: Icon(Icons.chevron_right),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.chevron_right), findsOneWidget);
    });
  });

  group('AppFeedback Tests', () {
    testWidgets('shows empty state', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppEmptyState(
              message: 'No items found',
              icon: Icons.inbox,
            ),
          ),
        ),
      );

      expect(find.text('No items found'), findsOneWidget);
      expect(find.byIcon(Icons.inbox), findsOneWidget);
    });

    testWidgets('shows error state', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppErrorState(
              message: 'Something went wrong',
              onRetry: () {},
            ),
          ),
        ),
      );

      expect(find.text('Something went wrong'), findsOneWidget);
      expect(find.text('重试'), findsOneWidget);
    });

    testWidgets('shows loading state', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: AppLoadingState(),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });
  });
}
