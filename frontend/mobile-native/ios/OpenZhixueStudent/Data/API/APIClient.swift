import Foundation
import Alamofire
import Combine

class APIClient {
    static let shared = APIClient()
    
    private let baseURL = "https://api.openzhixue.com/v1"
    private var session: Session
    private var cancellables = Set<AnyCancellable>()
    
    private init() {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 60
        
        session = Session(configuration: configuration)
    }
    
    private func getHeaders() -> HTTPHeaders {
        var headers: HTTPHeaders = [
            "Content-Type": "application/json"
        ]
        
        if let token = KeychainManager.shared.getToken() {
            headers["Authorization"] = "Bearer \(token)"
        }
        
        return headers
    }
    
    private func request<T: Codable>(_ endpoint: String,
                              method: HTTPMethod = .get,
                              parameters: Parameters? = nil) -> AnyPublisher<T, Error> {
        let url = "\(baseURL)\(endpoint)"
        
        return Future<T, Error> { [weak self] promise in
            guard let self = self else { return }
            
            self.session.request(url,
                                 method: method,
                                 parameters: parameters,
                                 encoding: JSONEncoding.default,
                                 headers: self.getHeaders())
            .validate()
            .responseDecodable(of: ApiResponse<T>.self) { response in
                switch response.result {
                case .success(let apiResponse):
                    if apiResponse.code == 0 {
                        promise(.success(apiResponse.data))
                    } else {
                        promise(.failure(APIError.serverError(apiResponse.message ?? "Unknown error")))
                    }
                case .failure(let error):
                    promise(.failure(self.handleError(error)))
                }
            }
        }
        .eraseToAnyPublisher()
    }
    
    private func requestAsync<T: Codable>(_ endpoint: String,
                                          method: HTTPMethod = .get,
                                          parameters: Parameters? = nil) async throws -> T {
        let url = "\(baseURL)\(endpoint)"
        
        return try await withCheckedThrowingContinuation { continuation in
            session.request(url,
                           method: method,
                           parameters: parameters,
                           encoding: JSONEncoding.default,
                           headers: getHeaders())
            .validate()
            .responseDecodable(of: ApiResponse<T>.self) { response in
                switch response.result {
                case .success(let apiResponse):
                    if apiResponse.code == 0 {
                        continuation.resume(returning: apiResponse.data)
                    } else {
                        continuation.resume(throwing: APIError.serverError(apiResponse.message ?? "Unknown error"))
                    }
                case .failure(let error):
                    continuation.resume(throwing: self.handleError(error))
                }
            }
        }
    }
    
    private func handleError(_ error: AFError) -> APIError {
        switch error {
        case .invalidURL:
            return .invalidURL
        case .connectionError:
            return .networkError
        case .responseValidationFailed:
            return .serverError("Response validation failed")
        default:
            return .unknown(error.localizedDescription)
        }
    }
}

struct ApiResponse<T: Codable>: Codable {
    let code: Int
    let message: String?
    let data: T
}

enum APIError: Error, LocalizedError {
    case invalidURL
    case networkError
    case serverError(String)
    case unauthorized
    case unknown(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidURL:
            return "Invalid URL"
        case .networkError:
            return "Network connection error"
        case .serverError(let message):
            return message
        case .unauthorized:
            return "Unauthorized access"
        case .unknown(let message):
            return message
        }
    }
}

extension APIClient {
    func login(username: String, password: String) async throws -> AuthResponse {
        let parameters: Parameters = [
            "username": username,
            "password": password
        ]
        return try await requestAsync("/auth/login", method: .post, parameters: parameters)
    }
    
    func logout() async throws -> EmptyResponse {
        return try await requestAsync("/auth/logout", method: .post)
    }
    
    func refreshToken() async throws -> AuthResponse {
        let parameters: Parameters = [
            "refreshToken": KeychainManager.shared.getRefreshToken() ?? ""
        ]
        return try await requestAsync("/auth/refresh", method: .post, parameters: parameters)
    }
    
    func getCurrentUser() async throws -> User {
        return try await requestAsync("/user/me")
    }
}

struct EmptyResponse: Codable {}

extension APIClient {
    func getHomework(status: String? = nil) async throws -> [Homework] {
        var endpoint = "/homework"
        if let status = status {
            endpoint += "?status=\(status)"
        }
        return try await requestAsync(endpoint)
    }
    
    func getHomeworkDetail(homeworkId: String) async throws -> Homework {
        return try await requestAsync("/homework/\(homeworkId)")
    }
    
    func submitHomework(homeworkId: String, content: String, attachments: [String]) async throws -> EmptyResponse {
        let parameters: Parameters = [
            "content": content,
            "attachments": attachments
        ]
        return try await requestAsync("/homework/\(homeworkId)/submit", method: .post, parameters: parameters)
    }
}

extension APIClient {
    func getGrades() async throws -> [GradeModel] {
        return try await requestAsync("/grades")
    }
    
    func getGradeDetail(gradeId: String) async throws -> GradeDetailModel {
        return try await requestAsync("/grades/\(gradeId)")
    }
}

extension APIClient {
    func getCourses() async throws -> [Course] {
        return try await requestAsync("/courses")
    }
    
    func getCourseDetail(courseId: String) async throws -> Course {
        return try await requestAsync("/courses/\(courseId)")
    }
    
    func getSchedule(weekStart: Date) async throws -> WeeklyScheduleModel {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd"
        let dateString = formatter.string(from: weekStart)
        return try await requestAsync("/schedule?week=\(dateString)")
    }
}

extension APIClient {
    func getMistakes() async throws -> [MistakeModel] {
        return try await requestAsync("/mistakes")
    }
    
    func getMistakeAnalysis(mistakeId: String) async throws -> MistakeAnalysisModel {
        return try await requestAsync("/mistakes/\(mistakeId)/analysis")
    }
    
    func getSimilarMistakes(mistakeId: String) async throws -> [MistakeModel] {
        return try await requestAsync("/mistakes/\(mistakeId)/similar")
    }
    
    func getResolveHistory(mistakeId: String) async throws -> [ResolveHistoryModel] {
        return try await requestAsync("/mistakes/\(mistakeId)/history")
    }
    
    func markMistakeResolved(mistakeId: String, note: String) async throws -> EmptyResponse {
        let parameters: Parameters = ["note": note]
        return try await requestAsync("/mistakes/\(mistakeId)/resolve", method: .post, parameters: parameters)
    }
    
    func toggleMistakeImportant(mistakeId: String) async throws -> EmptyResponse {
        return try await requestAsync("/mistakes/\(mistakeId)/important", method: .post)
    }
}

extension APIClient {
    func getNotifications() async throws -> [NotificationModel] {
        return try await requestAsync("/notifications")
    }
    
    func markNotificationAsRead(_ notificationId: String) async throws -> EmptyResponse {
        return try await requestAsync("/notifications/\(notificationId)/read", method: .post)
    }
    
    func markAllNotificationsAsRead() async throws -> EmptyResponse {
        return try await requestAsync("/notifications/read-all", method: .post)
    }
    
    func clearReadNotifications() async throws -> EmptyResponse {
        return try await requestAsync("/notifications/clear-read", method: .post)
    }
}

extension APIClient {
    func getAnalyticsOverview(period: String) async throws -> AnalyticsOverviewModel {
        return try await requestAsync("/analytics/overview?period=\(period)")
    }
    
    func getSubjectAnalysis(period: String) async throws -> [SubjectAnalysisModel] {
        return try await requestAsync("/analytics/subjects?period=\(period)")
    }
    
    func getScoreTrend(period: String) async throws -> [TrendDataModel] {
        return try await requestAsync("/analytics/trend/score?period=\(period)")
    }
    
    func getRankTrend(period: String) async throws -> [RankTrendModel] {
        return try await requestAsync("/analytics/trend/rank?period=\(period)")
    }
    
    func getSubjectDetails(period: String) async throws -> [SubjectDetailModel] {
        return try await requestAsync("/analytics/subjects/detail?period=\(period)")
    }
    
    func getStudySuggestions(period: String) async throws -> [StudySuggestionModel] {
        return try await requestAsync("/analytics/suggestions?period=\(period)")
    }
}

extension APIClient {
    func updateProfile(name: String?, avatar: String?) async throws -> User {
        var parameters: Parameters = [:]
        if let name = name {
            parameters["name"] = name
        }
        if let avatar = avatar {
            parameters["avatar"] = avatar
        }
        return try await requestAsync("/user/profile", method: .put, parameters: parameters)
    }
    
    func changePassword(oldPassword: String, newPassword: String) async throws -> EmptyResponse {
        let parameters: Parameters = [
            "oldPassword": oldPassword,
            "newPassword": newPassword
        ]
        return try await requestAsync("/user/password", method: .put, parameters: parameters)
    }
    
    func getSettings() async throws -> UserSettings {
        return try await requestAsync("/user/settings")
    }
    
    func updateSettings(_ settings: UserSettings) async throws -> UserSettings {
        let parameters: Parameters = [
            "notificationEnabled": settings.notificationEnabled,
            "homeworkReminder": settings.homeworkReminder,
            "gradeNotification": settings.gradeNotification,
            "darkMode": settings.darkMode,
            "language": settings.language
        ]
        return try await requestAsync("/user/settings", method: .put, parameters: parameters)
    }
}

struct UserSettings: Codable {
    let notificationEnabled: Bool
    let homeworkReminder: Bool
    let gradeNotification: Bool
    let darkMode: Bool
    let language: String
}
