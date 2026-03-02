package com.openzhixue.student.ui.screens.homework

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.FilterList
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.openzhixue.student.data.model.Homework
import com.openzhixue.student.ui.screens.home.EmptyState
import com.openzhixue.student.ui.screens.home.HomeworkItem
import com.openzhixue.student.ui.screens.home.StatusBadge

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeworkListScreen(
    viewModel: HomeworkListViewModel = hiltViewModel(),
    onHomeworkClick: (String) -> Unit
) {
    val homeworks by viewModel.homeworks.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("作业列表") },
                actions = {
                    IconButton(onClick = { }) {
                        Icon(Icons.Default.FilterList, contentDescription = "筛选")
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
        } else if (homeworks.isEmpty()) {
            EmptyState(message = "暂无作业")
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(homeworks) { homework ->
                    HomeworkItem(homework = homework)
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeworkDetailScreen(
    homeworkId: String,
    viewModel: HomeworkDetailViewModel = hiltViewModel(),
    onBack: () -> Unit
) {
    val homework by viewModel.homework.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("作业详情") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                }
            )
        }
    ) { padding ->
        homework?.let { hw ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(16.dp)
            ) {
                Text(
                    text = hw.title,
                    style = MaterialTheme.typography.headlineSmall
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = "${hw.courseName} · ${hw.teacherName}",
                    style = MaterialTheme.typography.bodyMedium
                )
                Spacer(modifier = Modifier.height(16.dp))
                Text(
                    text = hw.description,
                    style = MaterialTheme.typography.bodyLarge
                )
                Spacer(modifier = Modifier.height(16.dp))
                StatusBadge(status = hw.status)
            }
        }
    }
}
