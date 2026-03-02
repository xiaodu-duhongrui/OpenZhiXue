package com.openzhixue.student.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.openzhixue.student.ui.screens.home.HomeScreen
import com.openzhixue.student.ui.screens.homework.HomeworkListScreen
import com.openzhixue.student.ui.screens.homework.HomeworkDetailScreen
import com.openzhixue.student.ui.screens.grades.GradeListScreen
import com.openzhixue.student.ui.screens.grades.GradeDetailScreen
import com.openzhixue.student.ui.screens.courses.CourseListScreen
import com.openzhixue.student.ui.screens.courses.ScheduleScreen
import com.openzhixue.student.ui.screens.mistakes.MistakeListScreen
import com.openzhixue.student.ui.screens.mistakes.MistakeDetailScreen
import com.openzhixue.student.ui.screens.analytics.AnalyticsScreen
import com.openzhixue.student.ui.screens.notification.NotificationListScreen
import com.openzhixue.student.ui.screens.profile.ProfileScreen
import com.openzhixue.student.ui.screens.profile.SettingsScreen
import com.openzhixue.student.ui.screens.auth.LoginScreen

sealed class Screen(val route: String) {
    object Login : Screen("login")
    object Home : Screen("home")
    object HomeworkList : Screen("homework")
    object HomeworkDetail : Screen("homework/{homeworkId}")
    object GradeList : Screen("grades")
    object GradeDetail : Screen("grades/{gradeId}")
    object CourseList : Screen("courses")
    object Schedule : Screen("schedule")
    object MistakeList : Screen("mistakes")
    object MistakeDetail : Screen("mistakes/{mistakeId}")
    object Analytics : Screen("analytics")
    object NotificationList : Screen("notifications")
    object Profile : Screen("profile")
    object Settings : Screen("settings")
}

@Composable
fun AppNavigation(
    navController: NavHostController = rememberNavController()
) {
    NavHost(
        navController = navController,
        startDestination = Screen.Login.route
    ) {
        composable(Screen.Login.route) {
            LoginScreen(
                onLoginSuccess = {
                    navController.navigate(Screen.Home.route) {
                        popUpTo(Screen.Login.route) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Screen.Home.route) {
            HomeScreen(
                onNavigateToHomework = { navController.navigate(Screen.HomeworkList.route) },
                onNavigateToGrades = { navController.navigate(Screen.GradeList.route) },
                onNavigateToCourses = { navController.navigate(Screen.CourseList.route) },
                onNavigateToNotifications = { navController.navigate(Screen.NotificationList.route) },
                onNavigateToProfile = { navController.navigate(Screen.Profile.route) }
            )
        }
        
        composable(Screen.HomeworkList.route) {
            HomeworkListScreen(
                onHomeworkClick = { homeworkId ->
                    navController.navigate("homework/$homeworkId")
                }
            )
        }
        
        composable(Screen.HomeworkDetail.route) { backStackEntry ->
            val homeworkId = backStackEntry.arguments?.getString("homeworkId") ?: ""
            HomeworkDetailScreen(
                homeworkId = homeworkId,
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.GradeList.route) {
            GradeListScreen(
                onGradeClick = { gradeId ->
                    navController.navigate("grades/$gradeId")
                },
                onNavigateToAnalytics = {
                    navController.navigate(Screen.Analytics.route)
                }
            )
        }
        
        composable(Screen.GradeDetail.route) { backStackEntry ->
            val gradeId = backStackEntry.arguments?.getString("gradeId") ?: ""
            GradeDetailScreen(
                gradeId = gradeId,
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.CourseList.route) {
            CourseListScreen(
                onNavigateToSchedule = {
                    navController.navigate(Screen.Schedule.route)
                }
            )
        }
        
        composable(Screen.Schedule.route) {
            ScheduleScreen(
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.MistakeList.route) {
            MistakeListScreen(
                onMistakeClick = { mistakeId ->
                    navController.navigate("mistakes/$mistakeId")
                }
            )
        }
        
        composable(Screen.MistakeDetail.route) { backStackEntry ->
            val mistakeId = backStackEntry.arguments?.getString("mistakeId") ?: ""
            MistakeDetailScreen(
                mistakeId = mistakeId,
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.Analytics.route) {
            AnalyticsScreen(
                onBack = { navController.popBackStack() }
            )
        }
        
        composable(Screen.NotificationList.route) {
            NotificationListScreen()
        }
        
        composable(Screen.Profile.route) {
            ProfileScreen(
                onNavigateToSettings = {
                    navController.navigate(Screen.Settings.route)
                },
                onLogout = {
                    navController.navigate(Screen.Login.route) {
                        popUpTo(0) { inclusive = true }
                    }
                }
            )
        }
        
        composable(Screen.Settings.route) {
            SettingsScreen(
                onBack = { navController.popBackStack() }
            )
        }
    }
}
