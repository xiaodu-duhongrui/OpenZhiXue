package com.openzhixue.student.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.openzhixue.student.data.model.Homework
import com.openzhixue.student.data.model.HomeworkStatus
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeUiState(
    val userName: String = "同学",
    val pendingHomeworkCount: Int = 0,
    val unreadCount: Int = 0,
    val recentHomeworks: List<Homework> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

@HiltViewModel
class HomeViewModel @Inject constructor(
) : ViewModel() {
    
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()
    
    init {
        loadData()
    }
    
    private fun loadData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            
            _uiState.value = _uiState.value.copy(
                userName = "张三",
                pendingHomeworkCount = 3,
                unreadCount = 5,
                recentHomeworks = listOf(
                    Homework(
                        id = "1",
                        title = "数学作业第三章习题",
                        description = "完成课本第三章所有习题",
                        courseId = "math",
                        courseName = "数学",
                        teacherId = "t1",
                        teacherName = "王老师",
                        endTime = "2024-01-15T18:00:00",
                        status = HomeworkStatus.PENDING,
                        score = null,
                        feedback = null,
                        attachments = emptyList(),
                        submittedAt = null
                    ),
                    Homework(
                        id = "2",
                        title = "英语阅读理解练习",
                        description = "完成阅读理解练习册第10页",
                        courseId = "english",
                        courseName = "英语",
                        teacherId = "t2",
                        teacherName = "李老师",
                        endTime = "2024-01-14T18:00:00",
                        status = HomeworkStatus.SUBMITTED,
                        score = null,
                        feedback = null,
                        attachments = emptyList(),
                        submittedAt = "2024-01-13T15:00:00"
                    ),
                    Homework(
                        id = "3",
                        title = "物理实验报告",
                        description = "提交上周实验的报告",
                        courseId = "physics",
                        courseName = "物理",
                        teacherId = "t3",
                        teacherName = "张老师",
                        endTime = "2024-01-12T18:00:00",
                        status = HomeworkStatus.GRADED,
                        score = 95,
                        feedback = "实验报告完成得很好，数据分析准确",
                        attachments = emptyList(),
                        submittedAt = "2024-01-11T10:00:00"
                    )
                ),
                isLoading = false
            )
        }
    }
    
    fun refresh() {
        loadData()
    }
}
