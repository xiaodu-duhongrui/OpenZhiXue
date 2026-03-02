package com.openzhixue.student.ui.screens.grades

import androidx.lifecycle.ViewModel
import com.openzhixue.student.data.model.Grade
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class GradeListViewModel @Inject constructor(
) : ViewModel() {
    
    private val _grades = MutableStateFlow<List<Grade>>(emptyList())
    val grades: StateFlow<List<Grade>> = _grades.asStateFlow()
    
    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()
    
    init {
        loadGrades()
    }
    
    private fun loadGrades() {
        _isLoading.value = true
        _grades.value = listOf(
            Grade(
                id = "1",
                examId = "e1",
                examName = "期中考试",
                courseId = "math",
                courseName = "数学",
                score = 95.0,
                totalScore = 100.0,
                classRank = 3,
                classTotal = 45,
                gradeRank = 15,
                gradeTotal = 200,
                classAverage = 82.5,
                classHighest = 98.0,
                classLowest = 45.0,
                examDate = "2024-04-15",
                feedback = null
            ),
            Grade(
                id = "2",
                examId = "e1",
                examName = "期中考试",
                courseId = "english",
                courseName = "英语",
                score = 88.0,
                totalScore = 100.0,
                classRank = 8,
                classTotal = 45,
                gradeRank = 35,
                gradeTotal = 200,
                classAverage = 78.0,
                classHighest = 96.0,
                classLowest = 52.0,
                examDate = "2024-04-15",
                feedback = null
            )
        )
        _isLoading.value = false
    }
}

@HiltViewModel
class GradeDetailViewModel @Inject constructor(
) : ViewModel() {
    
    private val _grade = MutableStateFlow<Grade?>(null)
    val grade: StateFlow<Grade?> = _grade.asStateFlow()
    
    fun loadGrade(id: String) {
        _grade.value = Grade(
            id = id,
            examId = "e1",
            examName = "期中考试",
            courseId = "math",
            courseName = "数学",
            score = 95.0,
            totalScore = 100.0,
            classRank = 3,
            classTotal = 45,
            gradeRank = 15,
            gradeTotal = 200,
            classAverage = 82.5,
            classHighest = 98.0,
            classLowest = 45.0,
            examDate = "2024-04-15",
            feedback = "表现优秀，继续保持"
        )
    }
}
