import SwiftUI

@main
struct OpenZhixueApp: App {
    @StateObject private var appState = AppState()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .onAppear {
                    setupAppearance()
                    checkLoginStatus()
                }
        }
    }
    
    private func setupAppearance() {
        let appearance = UITabBarAppearance()
        appearance.configureWithDefaultBackground()
        UITabBar.appearance().standardAppearance = appearance
        UITabBar.appearance().scrollEdgeAppearance = appearance
        
        UINavigationBar.appearance().tintColor = UIColor(Color(hex: "1890FF"))
        
        UITableView.appearance().backgroundColor = UIColor(Color(hex: "F5F7FA"))
    }
    
    private func checkLoginStatus() {
        if let token = KeychainManager.shared.getToken(), !token.isEmpty {
            Task {
                do {
                    let user = try await APIClient.shared.getCurrentUser()
                    await MainActor.run {
                        appState.login(user: user)
                    }
                } catch {
                    KeychainManager.shared.clearTokens()
                }
            }
        }
    }
}
