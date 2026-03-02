package com.openzhixue.student.ui.screens.courses

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.openzhixue.student.data.model.Course
import com.openzhixue.student.ui.screens.home.EmptyState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CourseListScreen(
    viewModel: CourseListViewModel = hiltViewModel(),
    onNavigateToSchedule: () -> Unit
) {
    val courses by viewModel.courses.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("我的课程") },
                actions = {
                    IconButton(onClick = onNavigateToSchedule) {
                        Icon(Icons.Default.CalendarMonth, contentDescription = "课程表")
                    }
                }
            )
        }
    ) { padding ->
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                CircularProgressIndicator(modifier = Modifier.wrapContentSize())
            }
        } else if (courses.isEmpty()) {
            EmptyState(message = "暂无课程")
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(courses) { course ->
                    CourseItem(course = course)
                }
            }
        }
    }
}

@Composable
fun CourseItem(course: Course) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        onClick = { }
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = course.name,
                    style = MaterialTheme.typography.titleMedium
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "${course.teacherName} · ${course.credit}学分",
                    style = MaterialTheme.typography.bodySmall
                )
            }
            if (course.studentCount > 0) {
                Text(
                    text = "${course.studentCount}人",
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScheduleScreen(
    viewModel: ScheduleViewModel = hiltViewModel(),
    onBack: () -> Unit
) {
    var currentWeek by remember { mutableIntStateOf(1) }
    val weekdays = listOf("周一", "周二", "周三", "周四", "周五", "周六", "周日")
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("课程表") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                }
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                IconButton(
                    onClick = { if (currentWeek > 1) currentWeek-- }
                ) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "上一周")
                }
                
                Text(
                    text = "第 $currentWeek 周",
                    style = MaterialTheme.typography.titleMedium
                )
                
                IconButton(
                    onClick = { if (currentWeek < 20) currentWeek++ }
                ) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "下一周")
                }
            }
            
            Spacer(modifier = Modifier.height(16.dp))
            
            Text(
                text = "课程表功能开发中...",
                modifier = Modifier.fillMaxWidth(),
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}
