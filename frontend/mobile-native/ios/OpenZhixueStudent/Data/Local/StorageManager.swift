import Foundation
import Combine
import KeychainAccess

class KeychainManager {
    static let shared = KeychainManager()
    
    private let keychain = Keychain(service: "com.openzhixue.student")
    
    private init() {}
    
    func saveToken(_ token: String) {
        try? keychain.set(token, key: "auth_token")
    }
    
    func getToken() -> String? {
        return try? keychain.get("auth_token")
    }
    
    func saveRefreshToken(_ token: String) {
        try? keychain.set(token, key: "refresh_token")
    }
    
    func getRefreshToken() -> String? {
        return try? keychain.get("refresh_token")
    }
    
    func clearTokens() {
        try? keychain.remove("auth_token")
        try? keychain.remove("refresh_token")
    }
}

class UserDefaultsManager {
    static let shared = UserDefaultsManager()
    
    private let defaults = UserDefaults.standard
    
    private init() {}
    
    private enum Keys {
        static let userId = "user_id"
        static let userName = "user_name"
        static let userEmail = "user_email"
        static let userAvatar = "user_avatar"
        static let themeMode = "theme_mode"
        static let notificationEnabled = "notification_enabled"
    }
    
    func saveUser(_ user: User) {
        defaults.set(user.id, forKey: Keys.userId)
        defaults.set(user.name, forKey: Keys.userName)
        defaults.set(user.email, forKey: Keys.userEmail)
        defaults.set(user.avatar, forKey: Keys.userAvatar)
    }
    
    func getUser() -> User? {
        guard let id = defaults.string(forKey: Keys.userId),
              let name = defaults.string(forKey: Keys.userName) else {
            return nil
        }
        
        return User(
            id: id,
            name: name,
            email: defaults.string(forKey: Keys.userEmail),
            avatar: defaults.string(forKey: Keys.userAvatar),
            studentId: nil,
            className: nil
        )
    }
    
    func clearUser() {
        defaults.removeObject(forKey: Keys.userId)
        defaults.removeObject(forKey: Keys.userName)
        defaults.removeObject(forKey: Keys.userEmail)
        defaults.removeObject(forKey: Keys.userAvatar)
    }
    
    func setThemeMode(_ mode: String) {
        defaults.set(mode, forKey: Keys.themeMode)
    }
    
    func getThemeMode() -> String {
        return defaults.string(forKey: Keys.themeMode) ?? "system"
    }
    
    func setNotificationEnabled(_ enabled: Bool) {
        defaults.set(enabled, forKey: Keys.notificationEnabled)
    }
    
    func isNotificationEnabled() -> Bool {
        return defaults.bool(forKey: Keys.notificationEnabled)
    }
}
