package com.openzhixue.student.ui.screens.homework

import androidx.lifecycle.ViewModel
import com.openzhixue.student.data.model.Homework
import com.openzhixue.student.data.model.HomeworkStatus
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class HomeworkListViewModel @Inject constructor(
) : ViewModel() {
    
    private val _homeworks = MutableStateFlow<List<Homework>>(emptyList())
    val homeworks: StateFlow<List<Homework>> = _homeworks.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    init {
        loadHomeworks()
    }
    
    private fun loadHomeworks() {
        _isLoading.value = true
        _homeworks.value = listOf(
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
            )
        )
        _isLoading.value = false
    }
}

@HiltViewModel
class HomeworkDetailViewModel @Inject constructor(
) : ViewModel() {
    
    private val _homework = MutableStateFlow<Homework?>(null)
    val homework: StateFlow<Homework?> = _homework.asStateFlow()
    
    fun loadHomework(id: String) {
        _homework.value = Homework(
            id = id,
            title = "数学作业第三章习题",
            description = "完成课本第三章所有习题，包括课后练习和拓展题",
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
        )
    }
}
