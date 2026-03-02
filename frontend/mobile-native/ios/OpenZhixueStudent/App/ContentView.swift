import SwiftUI
import Combine

struct ContentView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        if appState.isLoggedIn {
            MainTabView()
        } else {
            LoginView()
        }
    }
}

struct MainTabView: View {
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        TabView(selection: Binding(
            get: { appState.selectedTab },
            set: { appState.selectedTab = $0 }
        )) {
            HomeView()
                .tabItem {
                    Image(systemName: "house.fill")
                    Text("首页")
                }
                .tag(AppState.Tab.home)
            
            HomeworkListView()
                .tabItem {
                    Image(systemName: "doc.text.fill")
                    Text("作业")
                }
                .tag(AppState.Tab.homework)
            
            GradeListView()
                .tabItem {
                    Image(systemName: "chart.bar.fill")
                    Text("成绩")
                }
                .tag(AppState.Tab.grades)
            
            MistakeListView()
                .tabItem {
                    Image(systemName: "book.fill")
                    Text("错题")
                }
                .tag(AppState.Tab.mistakes)
            
            ProfileView()
                .tabItem {
                    Image(systemName: "person.fill")
                    Text("我的")
                }
                .tag(AppState.Tab.profile)
        }
        .tint(Color(hex: "1890FF"))
    }
}

class AppState: ObservableObject {
    enum Tab: Int {
        case home
        case homework
        case grades
        case mistakes
        case profile
    }
    
    @Published var isLoggedIn: Bool = false
    @Published var selectedTab: Tab = .home
    @Published var currentUser: User?
    @Published var unreadNotificationCount: Int = 0
    
    func login(user: User) {
        currentUser = user
        isLoggedIn = true
    }
    
    func logout() {
        currentUser = nil
        isLoggedIn = false
        selectedTab = .home
    }
}

#if DEBUG
struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
            .environmentObject(AppState())
    }
}
#endif
