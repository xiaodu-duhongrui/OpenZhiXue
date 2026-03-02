package com.openzhixue.student

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class OpenZhixueApp : Application() {
    override fun onCreate() {
        super.onCreate()
    }
}
