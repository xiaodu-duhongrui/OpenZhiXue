package com.openzhixue.student.ui.screens.courses

import androidx.lifecycle.ViewModel
import com.openzhixue.student.data.model.Course
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class CourseListViewModel @Inject constructor(
) : ViewModel() {
    
    private val _courses = MutableStateFlow<List<Course>>(emptyList())
    val courses: StateFlow<List<Course>> = _courses.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    init {
        loadCourses()
    }
    
    private fun loadCourses() {
        _isLoading.value = true
        _courses.value = listOf(
            Course(
                id = "1",
                name = "高等数学",
                code = "MATH101",
                teacherId = "t1",
                teacherName = "王老师",
                credit = 4,
                description = "高等数学课程",
                academicYear = "2023-2024",
                semester = 1,
                studentCount = 45
            ),
            Course(
                id = "2",
                name = "大学英语",
                code = "ENG101",
                teacherId = "t2",
                teacherName = "李老师",
                credit = 3,
                description = "大学英语课程",
                academicYear = "2023-2024",
                semester = 1,
                studentCount = 42
            ),
            Course(
                id = "3",
                name = "大学物理",
                code = "PHY101",
                teacherId = "t3",
                teacherName = "张老师",
                credit = 3,
                description = "大学物理课程",
                academicYear = "2023-2024",
                semester = 1,
                studentCount = 48
            )
        )
        _isLoading.value = false
    }
}

@HiltViewModel
class ScheduleViewModel @Inject constructor(
) : ViewModel()
