import SwiftUI
import Combine

struct HomeView: View {
    @StateObject private var viewModel = HomeViewModel()
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 16) {
                    WelcomeCard(
                        userName: viewModel.userName,
                        pendingHomeworkCount: viewModel.pendingHomeworkCount
                    )
                    
                    QuickActionsSection(
                        onHomeworkTap: { appState.selectedTab = .homework },
                        onGradesTap: { appState.selectedTab = .grades },
                        onMistakesTap: { appState.selectedTab = .mistakes },
                        onNotificationTap: { }
                    )
                    
                    StudyProgressCard(progress: viewModel.studyProgress)
                    
                    if !viewModel.recentHomeworks.isEmpty {
                        RecentHomeworkSection(homeworks: viewModel.recentHomeworks)
                    }
                    
                    if !viewModel.upcomingExams.isEmpty {
                        UpcomingExamsSection(exams: viewModel.upcomingExams)
                    }
                    
                    QuickLinksSection()
                }
                .padding()
            }
            .background(Color(hex: "F5F7FA"))
            .navigationTitle("智学")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    HStack(spacing: 16) {
                        NavigationLink(destination: NotificationListView()) {
                            ZStack(alignment: .topTrailing) {
                                Image(systemName: "bell.fill")
                                    .foregroundColor(.primary)
                                
                                if viewModel.unreadCount > 0 {
                                    Circle()
                                        .fill(Color.red)
                                        .frame(width: 10, height: 10)
                                        .offset(x: 4, y: -4)
                                }
                            }
                        }
                        
                        NavigationLink(destination: AnalyticsView()) {
                            Image(systemName: "chart.line.uptrend.xyaxis")
                                .foregroundColor(.primary)
                        }
                    }
                }
            }
            .refreshable {
                await viewModel.refresh()
            }
        }
        .task {
            await viewModel.loadData()
        }
    }
}

struct WelcomeCard: View {
    let userName: String
    let pendingHomeworkCount: Int
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 8) {
                Text("你好，\(userName)")
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(.white)
                
                Text(greetingMessage)
                    .font(.subheadline)
                    .foregroundColor(.white.opacity(0.9))
                
                HStack(spacing: 24) {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("\(pendingHomeworkCount)")
                            .font(.title)
                            .fontWeight(.bold)
                            .foregroundColor(.white)
                        Text("待完成作业")
                            .font(.caption)
                            .foregroundColor(.white.opacity(0.8))
                    }
                }
                .padding(.top, 8)
            }
            
            Spacer()
            
            Image(systemName: "graduationcap.fill")
                .font(.system(size: 60))
                .foregroundColor(.white.opacity(0.3))
        }
        .padding()
        .background(
            LinearGradient(
                colors: [Color(hex: "1890FF"), Color(hex: "096DD9")],
                startPoint: .topLeading,
                endPoint: .bottomTrailing
            )
        )
        .cornerRadius(16)
        .shadow(color: Color(hex: "1890FF").opacity(0.3), radius: 8, x: 0, y: 4)
    }
    
    private var greetingMessage: String {
        let hour = Calendar.current.component(.hour, from: Date())
        if hour < 12 { return "早上好，今天也要加油哦！" }
        if hour < 18 { return "下午好，继续努力学习！" }
        return "晚上好，记得复习今天的内容！"
    }
}

struct QuickActionsSection: View {
    let onHomeworkTap: () -> Void
    let onGradesTap: () -> Void
    let onMistakesTap: () -> Void
    let onNotificationTap: () -> Void
    
    var body: some View {
        HStack(spacing: 12) {
            QuickActionButton(
                icon: "doc.text.fill",
                label: "作业",
                color: Color(hex: "1890FF"),
                action: onHomeworkTap
            )
            
            QuickActionButton(
                icon: "chart.bar.fill",
                label: "成绩",
                color: Color(hex: "52C41A"),
                action: onGradesTap
            )
            
            QuickActionButton(
                icon: "book.fill",
                label: "错题本",
                color: Color(hex: "FA8C16"),
                action: onMistakesTap
            )
            
            QuickActionButton(
                icon: "bell.fill",
                label: "消息",
                color: Color(hex: "722ED1"),
                action: onNotificationTap
            )
        }
    }
}

struct QuickActionButton: View {
    let icon: String
    let label: String
    let color: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            VStack(spacing: 8) {
                ZStack {
                    RoundedRectangle(cornerRadius: 12)
                        .fill(color.opacity(0.1))
                        .frame(width: 56, height: 56)
                    
                    Image(systemName: icon)
                        .font(.title3)
                        .foregroundColor(color)
                }
                
                Text(label)
                    .font(.caption)
                    .foregroundColor(.primary)
            }
            .frame(maxWidth: .infinity)
        }
    }
}

struct StudyProgressCard: View {
    let progress: StudyProgressModel
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("学习进度")
                    .font(.headline)
                
                Spacer()
                
                Text("本周")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            HStack(spacing: 16) {
                ProgressItem(title: "作业完成", current: progress.homeworkCompleted, total: progress.homeworkTotal, color: Color(hex: "1890FF"))
                ProgressItem(title: "错题攻克", current: progress.mistakesResolved, total: progress.mistakesTotal, color: Color(hex: "52C41A"))
                ProgressItem(title: "学习天数", current: progress.studyDays, total: 7, color: Color(hex: "FA8C16"))
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct ProgressItem: View {
    let title: String
    let current: Int
    let total: Int
    let color: Color
    
    var body: some View {
        VStack(spacing: 6) {
            ZStack {
                Circle()
                    .stroke(Color(hex: "E8E8E8"), lineWidth: 4)
                    .frame(width: 50, height: 50)
                
                Circle()
                    .trim(from: 0, to: total > 0 ? CGFloat(current) / CGFloat(total) : 0)
                    .stroke(color, style: StrokeStyle(lineWidth: 4, lineCap: .round))
                    .frame(width: 50, height: 50)
                    .rotationEffect(.degrees(-90))
                
                Text("\(current)")
                    .font(.caption)
                    .fontWeight(.semibold)
                    .foregroundColor(color)
            }
            
            Text(title)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

struct RecentHomeworkSection: View {
    let homeworks: [Homework]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("最近作业")
                    .font(.headline)
                
                Spacer()
            }
            
            ForEach(homeworks.prefix(3)) { homework in
                HomeworkItemView(homework: homework)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct HomeworkItemView: View {
    let homework: Homework
    
    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 4) {
                Text(homework.title)
                    .font(.subheadline)
                    .fontWeight(.medium)
                    .lineLimit(1)
                
                Text(homework.courseName)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text(statusText)
                    .font(.caption)
                    .padding(.horizontal, 8)
                    .padding(.vertical, 4)
                    .background(statusColor.opacity(0.1))
                    .foregroundColor(statusColor)
                    .cornerRadius(4)
                
                Text(formatDeadline(homework.endTime))
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding(.vertical, 8)
    }
    
    private var statusText: String {
        switch homework.status {
        case .pending: return "待完成"
        case .submitted: return "已提交"
        case .graded: return "已批改"
        case .late: return "已逾期"
        }
    }
    
    private var statusColor: Color {
        switch homework.status {
        case .pending: return Color(hex: "FAAD14")
        case .submitted: return Color(hex: "1890FF")
        case .graded: return Color(hex: "52C41A")
        case .late: return Color(hex: "F5222D")
        }
    }
    
    private func formatDeadline(_ deadline: String) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        if let date = formatter.date(from: deadline) {
            let displayFormatter = DateFormatter()
            displayFormatter.dateFormat = "MM-dd HH:mm"
            return displayFormatter.string(from: date)
        }
        return deadline
    }
}

struct UpcomingExamsSection: View {
    let exams: [UpcomingExamModel]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("即将考试")
                    .font(.headline)
                
                Spacer()
            }
            
            ForEach(exams) { exam in
                HStack(spacing: 12) {
                    Image(systemName: "calendar.badge.clock")
                        .foregroundColor(Color(hex: "F5222D"))
                    
                    VStack(alignment: .leading, spacing: 2) {
                        Text(exam.name)
                            .font(.subheadline)
                            .fontWeight(.medium)
                        
                        Text(exam.date)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    Text(exam.daysLeft > 0 ? "\(exam.daysLeft)天后" : "今天")
                        .font(.caption)
                        .foregroundColor(exam.daysLeft <= 3 ? .red : .secondary)
                }
                .padding(.vertical, 8)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct QuickLinksSection: View {
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("快捷入口")
                .font(.headline)
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 4), spacing: 16) {
                QuickLinkItem(icon: "calendar", label: "课程表")
                QuickLinkItem(icon: "doc.text.magnifyingglass", label: "试卷查看")
                QuickLinkItem(icon: "lightbulb", label: "学习建议")
                QuickLinkItem(icon: "questionmark.circle", label: "帮助中心")
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct QuickLinkItem: View {
    let icon: String
    let label: String
    
    var body: some View {
        VStack(spacing: 6) {
            Image(systemName: icon)
                .font(.title3)
                .foregroundColor(Color(hex: "1890FF"))
            
            Text(label)
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

struct StudyProgressModel {
    let homeworkCompleted: Int
    let homeworkTotal: Int
    let mistakesResolved: Int
    let mistakesTotal: Int
    let studyDays: Int
}

struct UpcomingExamModel: Identifiable {
    let id: String
    let name: String
    let date: String
    let daysLeft: Int
}

@MainActor
class HomeViewModel: ObservableObject {
    @Published var userName: String = "同学"
    @Published var pendingHomeworkCount: Int = 0
    @Published var unreadCount: Int = 0
    @Published var recentHomeworks: [Homework] = []
    @Published var upcomingExams: [UpcomingExamModel] = []
    @Published var studyProgress: StudyProgressModel = StudyProgressModel(homeworkCompleted: 0, homeworkTotal: 0, mistakesResolved: 0, mistakesTotal: 0, studyDays: 0)
    @Published var isLoading: Bool = false
    
    func loadData() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            async let homeworkTask = APIClient.shared.getHomework(status: "pending")
            
            let homeworks = try await homeworkTask
            await MainActor.run {
                self.pendingHomeworkCount = homeworks.count
                self.recentHomeworks = Array(homeworks.prefix(5))
            }
        } catch {
            print("Error loading home data: \(error)")
        }
    }
    
    func refresh() async {
        await loadData()
    }
}

struct HomeView_Previews: PreviewProvider {
    static var previews: some View {
        HomeView()
            .environmentObject(AppState())
    }
}
