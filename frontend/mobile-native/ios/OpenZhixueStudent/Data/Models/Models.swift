import Foundation
import Combine

struct User: Codable {
    let id: String
    let name: String
    let email: String?
    let avatar: String?
    let studentId: String?
    let className: String?
}

struct AuthResponse: Codable {
    let token: String
    let refreshToken: String
    let expiresIn: Int
    let user: User
}

struct Homework: Codable, Identifiable {
    let id: String
    let title: String
    let description: String
    let courseId: String
    let courseName: String
    let teacherId: String
    let teacherName: String
    let endTime: String
    let status: HomeworkStatus
    let score: Int?
    let feedback: String?
    let attachments: [String]
    let submittedAt: String?
}

enum HomeworkStatus: String, Codable {
    case pending = "pending"
    case submitted = "submitted"
    case graded = "graded"
    case late = "late"
}

struct GradeModel: Codable, Identifiable {
    let id: String
    let examId: String
    let examName: String
    let subject: String
    let score: Double
    let totalScore: Double
    let rank: Int
    let totalStudents: Int
    let date: String
    let semester: String
}

struct GradeDetailModel: Codable {
    let classAverage: Double
    let classHighest: Double
    let classLowest: Double
    let gradeAverage: Double
    let gradeHighest: Double
    let gradeLowest: Double
    let questions: [QuestionScoreModel]
    let rankDistribution: [RankDistributionModel]
}

struct QuestionScoreModel: Codable, Identifiable {
    let id: String
    let number: Int
    let score: Double
    let maxScore: Double
}

struct RankDistributionModel: Codable, Identifiable {
    let id: String
    let range: String
    let count: Int
    let percentage: Double
}

struct Course: Codable, Identifiable {
    let id: String
    let name: String
    let code: String
    let teacherId: String
    let teacherName: String
    let credit: Int
    let description: String?
    let academicYear: String
    let semester: Int
    let studentCount: Int
}

struct CourseSchedule: Codable {
    let courseId: String
    let courseName: String
    let teacherName: String
    let location: String
    let weekday: Int
    let startPeriod: Int
    let endPeriod: Int
    let weekStart: Int
    let weekEnd: Int
}

struct MistakeModel: Codable, Identifiable {
    let id: String
    let questionId: String
    let content: String
    let correctAnswer: String
    let wrongAnswer: String
    let subject: String
    let source: String
    let images: [String]
    let createdAt: String
    let isResolved: Bool
    let isImportant: Bool
}

struct MistakeStatsModel: Codable {
    let total: Int
    let unresolved: Int
    let resolved: Int
    let important: Int
}

struct MistakeAnalysisModel: Codable {
    let errorTypes: [String]
    let knowledgePoints: [String]
    let analysis: String
}

struct ResolveHistoryModel: Codable, Identifiable {
    let id: String
    let date: String
    let note: String
}

struct NotificationModel: Codable, Identifiable {
    let id: String
    let title: String
    let content: String
    let type: NotificationType
    let isRead: Bool
    let time: String
    let isActionable: Bool
}

enum NotificationType: String, Codable {
    case system = "system"
    case homework = "homework"
    case grade = "grade"
    case course = "course"
}

struct AnalyticsOverviewModel: Codable {
    let averageScore: Double
    let rank: Int
    let progress: Int
    let homeworkCompletion: Int
    let mistakeCount: Int
    let studyDays: Int
}

struct SubjectAnalysisModel: Codable, Identifiable {
    let id: String
    let subject: String
    let score: Double
}

struct TrendDataModel: Codable, Identifiable {
    let id: String
    let date: String
    let score: Double
}

struct RankTrendModel: Codable, Identifiable {
    let id: String
    let date: String
    let rank: Int
}

struct SubjectDetailModel: Codable, Identifiable {
    let id: String
    let subject: String
    let averageScore: Double
    let examCount: Int
    let trend: Int
}

struct StudySuggestionModel: Codable, Identifiable {
    let id: String
    let icon: String
    let title: String
    let content: String
}

struct WeeklyScheduleModel: Codable {
    let courses: [String: ScheduleCourseModel]
    
    func getCourse(day: Int, slot: Int) -> ScheduleCourseModel? {
        let key = "\(day)-\(slot)"
        return courses[key]
    }
}

struct ScheduleCourseModel: Codable {
    let name: String
    let teacher: String
    let room: String
}

struct LearningAnalytics: Codable {
    let studentId: String
    let studentName: String
    let generateTime: String
    let subjectAnalyses: [SubjectAnalysis]
    let overall: OverallAnalysis
    let knowledgePoints: [KnowledgePoint]
    let scoreTrends: [ScoreTrend]
    let suggestions: [StudySuggestion]
}

struct SubjectAnalysis: Codable {
    let subjectId: String
    let subjectName: String
    let averageScore: Double
    let rank: Int
    let totalStudents: Int
}

struct KnowledgePoint: Codable {
    let id: String
    let name: String
    let masteryLevel: Double
    let subjectId: String
    let subjectName: String
}

struct OverallAnalysis: Codable {
    let totalAverage: Double
    let totalExams: Int
    let improvedSubjects: Int
    let declinedSubjects: Int
    let overallLevel: String
}

struct ScoreTrend: Codable {
    let examId: String
    let examName: String
    let examDate: String
    let score: Double
    let averageScore: Double
    let rank: Int
}

struct StudySuggestion: Codable {
    let subjectId: String
    let subjectName: String
    let suggestion: String
    let priority: Int
}
