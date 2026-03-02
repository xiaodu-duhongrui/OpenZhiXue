package com.openzhixue.student.data.api

import com.openzhixue.student.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface AuthApi {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): Response<ApiResponse<AuthResponse>>
    
    @POST("auth/logout")
    suspend fun logout(): Response<ApiResponse<Unit>>
    
    @POST("auth/refresh")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<ApiResponse<AuthResponse>>
}

interface HomeworkApi {
    @GET("homework")
    suspend fun getHomeworkList(@QueryMap params: Map<String, String>): Response<ApiResponse<List<Homework>>>
    
    @GET("homework/{id}")
    suspend fun getHomeworkDetail(@Path("id") id: String): Response<ApiResponse<Homework>>
    
    @POST("homework/{id}/submit")
    suspend fun submitHomework(@Path("id") id: String, @Body request: SubmitHomeworkRequest): Response<ApiResponse<Unit>>
}

interface GradeApi {
    @GET("grades")
    suspend fun getGradeList(@QueryMap params: Map<String, String>): Response<ApiResponse<List<Grade>>>
    
    @GET("grades/{id}")
    suspend fun getGradeDetail(@Path("id") id: String): Response<ApiResponse<Grade>>
    
    @GET("grades/trends")
    suspend fun getGradeTrends(@Query("subjectId") subjectId: String?): Response<ApiResponse<List<ScoreTrend>>>
    
    @GET("grades/analysis")
    suspend fun getGradeAnalysis(): Response<ApiResponse<LearningAnalytics>>
}

interface CourseApi {
    @GET("courses")
    suspend fun getCourseList(@QueryMap params: Map<String, String>): Response<ApiResponse<List<Course>>>
    
    @GET("courses/{id}")
    suspend fun getCourseDetail(@Path("id") id: String): Response<ApiResponse<Course>>
    
    @GET("courses/schedule")
    suspend fun getCourseSchedule(): Response<ApiResponse<List<CourseSchedule>>>
}

interface MistakeApi {
    @GET("mistakes")
    suspend fun getMistakes(@QueryMap params: Map<String, String>): Response<ApiResponse<List<Mistake>>>
    
    @GET("mistakes/{id}")
    suspend fun getMistakeDetail(@Path("id") id: String): Response<ApiResponse<Mistake>>
    
    @POST("mistakes/{id}/practice")
    suspend fun submitPractice(@Path("id") id: String, @Body request: PracticeRequest): Response<ApiResponse<Mistake>>
    
    @POST("mistakes/export")
    suspend fun exportPdf(@Body params: Map<String, Any>): Response<ApiResponse<ExportResult>>
}

interface NotificationApi {
    @GET("notifications")
    suspend fun getNotifications(@QueryMap params: Map<String, String>): Response<ApiResponse<List<AppNotification>>>
    
    @GET("notifications/{id}")
    suspend fun getNotificationDetail(@Path("id") id: String): Response<ApiResponse<AppNotification>>
    
    @POST("notifications/{id}/read")
    suspend fun markAsRead(@Path("id") id: String): Response<ApiResponse<Unit>>
    
    @POST("notifications/read-all")
    suspend fun markAllAsRead(): Response<ApiResponse<Unit>>
}
