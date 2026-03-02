package com.openzhixue.student.ui.screens.grades

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.openzhixue.student.data.model.Grade
import com.openzhixue.student.ui.screens.home.EmptyState

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GradeListScreen(
    viewModel: GradeListViewModel = hiltViewModel(),
    onGradeClick: (String) -> Unit,
    onNavigateToAnalytics: () -> Unit
) {
    val grades by viewModel.grades.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("成绩查询") },
                actions = {
                    IconButton(onClick = onNavigateToAnalytics) {
                        Icon(Icons.Default.BarChart, contentDescription = "分析")
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
        } else if (grades.isEmpty()) {
            EmptyState(message = "暂无成绩记录")
        } else {
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                items(grades) { grade ->
                    GradeItem(grade = grade)
                }
            }
        }
    }
}

@Composable
fun GradeItem(grade: Grade) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        onClick = { }
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = grade.examName,
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = "${grade.score}/${grade.totalScore}",
                    style = MaterialTheme.typography.titleMedium,
                    color = getScoreColor(grade.score, grade.totalScore)
                )
            }
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = grade.courseName,
                style = MaterialTheme.typography.bodySmall
            )
            if (grade.classRank != null) {
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = "班级第${grade.classRank}名",
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GradeDetailScreen(
    gradeId: String,
    viewModel: GradeDetailViewModel = hiltViewModel(),
    onBack: () -> Unit
) {
    val grade by viewModel.grade.collectAsState()
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("成绩详情") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "返回")
                    }
                }
            )
        }
    ) { padding ->
        grade?.let { g ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(16.dp)
            ) {
                Text(
                    text = g.examName,
                    style = MaterialTheme.typography.headlineSmall
                )
                Spacer(modifier = Modifier.height(8.dp))
                Text(
                    text = g.courseName,
                    style = MaterialTheme.typography.bodyLarge
                )
                Spacer(modifier = Modifier.height(24.dp))
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.Center
                ) {
                    Text(
                        text = g.score.toString(),
                        style = MaterialTheme.typography.displayLarge,
                        color = getScoreColor(g.score, g.totalScore)
                    )
                    Text(
                        text = " / ${g.totalScore}",
                        style = MaterialTheme.typography.headlineMedium
                    )
                }
            }
        }
    }
}

fun getScoreColor(score: Double, totalScore: Double): androidx.compose.ui.graphics.Color {
    val percentage = score / totalScore * 100
    return when {
        percentage >= 90 -> androidx.compose.ui.graphics.Color(0xFF4CAF50)
        percentage >= 80 -> androidx.compose.ui.graphics.Color(0xFF2196F3)
        percentage >= 60 -> androidx.compose.ui.graphics.Color(0xFFFF9800)
        else -> androidx.compose.ui.graphics.Color(0xFFF44336)
    }
}
