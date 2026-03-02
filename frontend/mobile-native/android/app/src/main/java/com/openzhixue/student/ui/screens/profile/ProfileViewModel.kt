package com.openzhixue.student.ui.screens.profile

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

@HiltViewModel
class ProfileViewModel @Inject constructor(
) : ViewModel() {
    
    private val _userName = MutableStateFlow("张三")
    val userName: StateFlow<String> = _userName.asStateFlow()
    
    private val _className = MutableStateFlow("高三(1)班")
    val className: StateFlow<String> = _className.asStateFlow()
    
    fun logout() {
    }
}

@HiltViewModel
class SettingsViewModel @Inject constructor(
) : ViewModel()
