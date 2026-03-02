package com.openzhixue.student.ui.screens.home

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.openzhixue.student.data.model.Homework
import com.openzhixue.student.data.model.HomeworkStatus
import com.openzhixue.student.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    viewModel: HomeViewModel = hiltViewModel(),
    onNavigateToHomework: () -> Unit,
    onNavigateToGrades: () -> Unit,
    onNavigateToCourses: () -> Unit,
    onNavigateToNotifications: () -> Unit,
    onNavigateToProfile: () -> Unit
) {
    val uiState by viewModel.uiState.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("智学") },
                actions = {
                    IconButton(onClick = onNavigateToNotifications) {
                        BadgedBox(
                            badge = {
                                if (uiState.unreadCount > 0) {
                                    Badge { Text(uiState.unreadCount.toString()) }
                                }
                            }
                        ) {
                            Icon(Icons.Default.Notifications, contentDescription = "通知")
                        }
                    }
                    IconButton(onClick = onNavigateToProfile) {
                        Icon(Icons.Default.Person, contentDescription = "个人中心")
                    }
                }
            )
        }
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            item {
                WelcomeCard(
                    userName = uiState.userName,
                    pendingHomeworkCount = uiState.pendingHomeworkCount
                )
            }
            
            item {
                QuickActionsSection(
                    onHomeworkClick = onNavigateToHomework,
                    onGradesClick = onNavigateToGrades,
                    onCoursesClick = onNavigateToCourses,
                    onNotificationsClick = onNavigateToNotifications
                )
            }
            
            item {
                Text(
                    text = "最近作业",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
            }
            
            if (uiState.recentHomeworks.isEmpty()) {
                item {
                    EmptyState(message = "暂无作业")
                }
            } else {
                items(uiState.recentHomeworks) { homework ->
                    HomeworkItem(homework = homework)
                }
            }
        }
    }
}

@Composable
fun WelcomeCard(
    userName: String,
    pendingHomeworkCount: Int
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primary
        )
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(20.dp)
        ) {
            Text(
                text = "你好，$userName",
                style = MaterialTheme.typography.titleLarge,
                color = Color.White
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "今天有 $pendingHomeworkCount 项作业待完成",
                style = MaterialTheme.typography.bodyMedium,
                color = Color.White.copy(alpha = 0.8f)
            )
        }
    }
}

@Composable
fun QuickActionsSection(
    onHomeworkClick: () -> Unit,
    onGradesClick: () -> Unit,
    onCoursesClick: () -> Unit,
    onNotificationsClick: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceEvenly
    ) {
        QuickActionButton(
            icon = Icons.Default.Assignment,
            label = "作业",
            color = Info,
            onClick = onHomeworkClick
        )
        QuickActionButton(
            icon = Icons.Default.Grading,
            label = "成绩",
            color = Success,
            onClick = onGradesClick
        )
        QuickActionButton(
            icon = Icons.Default.Schedule,
            label = "课表",
            color = Warning,
            onClick = onCoursesClick
        )
        QuickActionButton(
            icon = Icons.Default.Message,
            label = "消息",
            color = Secondary,
            onClick = onNotificationsClick
        )
    }
}

@Composable
fun QuickActionButton(
    icon: ImageVector,
    label: String,
    color: Color,
    onClick: () -> Unit
) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        FilledTonalButton(
            onClick = onClick,
            modifier = Modifier.size(56.dp),
            shape = MaterialTheme.shapes.medium,
            colors = ButtonDefaults.filledTonalButtonColors(
                containerColor = color.copy(alpha = 0.1f)
            )
        ) {
            Icon(
                icon,
                contentDescription = label,
                tint = color,
                modifier = Modifier.size(24.dp)
            )
        }
        Spacer(modifier = Modifier.height(4.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall
        )
    }
}

@Composable
fun HomeworkItem(homework: Homework) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        onClick = { }
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = homework.title,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Medium
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = homework.courseName,
                    style = MaterialTheme.typography.bodySmall,
                    color = TextSecondary
                )
            }
            StatusBadge(status = homework.status)
        }
    }
}

@Composable
fun StatusBadge(status: HomeworkStatus) {
    val (text, color) = when (status) {
        HomeworkStatus.PENDING -> "待完成" to Warning
        HomeworkStatus.SUBMITTED -> "已提交" to Info
        HomeworkStatus.GRADED -> "已批改" to Success
        HomeworkStatus.LATE -> "已逾期" to Danger
    }
    
    Surface(
        shape = MaterialTheme.shapes.small,
        color = color.copy(alpha = 0.1f)
    ) {
        Text(
            text = text,
            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
            style = MaterialTheme.typography.labelSmall,
            color = color
        )
    }
}

@Composable
fun EmptyState(message: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .padding(32.dp),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Icon(
                Icons.Default.Inbox,
                contentDescription = null,
                modifier = Modifier.size(64.dp),
                tint = TextHint
            )
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondary
            )
        }
    }
}
