package com.openzhixue.student.ui.screens.mistakes

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun MistakeListScreen(
    viewModel: MistakeListViewModel = hiltViewModel(),
    onMistakeClick: (String) -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("错题本") })
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            Text("错题本功能开发中...")
        }
    }
}

@Composable
fun MistakeDetailScreen(
    mistakeId: String,
    viewModel: MistakeDetailViewModel = hiltViewModel(),
    onBack: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(title = { Text("错题详情") })
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            Text("错题详情功能开发中...")
        }
    }
}
