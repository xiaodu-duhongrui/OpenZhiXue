import SwiftUI

struct NotificationListView: View {
    @StateObject private var viewModel = NotificationViewModel()
    @State private var selectedType: NotificationFilterType = .all
    @State private var showUnreadOnly = false
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(hex: "F5F7FA")
                    .ignoresSafeArea()
                
                if viewModel.isLoading {
                    ProgressView("加载中...")
                } else if viewModel.notifications.isEmpty {
                    EmptyStateView(
                        icon: "bell.slash",
                        title: "暂无通知",
                        subtitle: "新消息会显示在这里"
                    )
                } else {
                    ScrollView {
                        VStack(spacing: 12) {
                            NotificationFilterView(
                                selectedType: $selectedType,
                                showUnreadOnly: $showUnreadOnly,
                                unreadCount: viewModel.unreadCount
                            )
                            
                            LazyVStack(spacing: 12) {
                                ForEach(filteredNotifications) { notification in
                                    NotificationCardView(notification: notification)
                                        .onTapGesture {
                                            viewModel.markAsRead(notification.id)
                                        }
                                }
                            }
                        }
                        .padding()
                    }
                    .refreshable {
                        await viewModel.loadNotifications()
                    }
                }
            }
            .navigationTitle("消息通知")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button(action: { viewModel.markAllAsRead() }) {
                            Label("全部已读", systemImage: "checkmark.circle")
                        }
                        
                        Button(action: { viewModel.clearReadNotifications() }) {
                            Label("清除已读", systemImage: "trash")
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
        }
        .task {
            await viewModel.loadNotifications()
        }
    }
    
    var filteredNotifications: [NotificationModel] {
        var result = viewModel.notifications
        
        switch selectedType {
        case .all:
            break
        case .homework:
            result = result.filter { $0.type == .homework }
        case .grade:
            result = result.filter { $0.type == .grade }
        case .system:
            result = result.filter { $0.type == .system }
        case .course:
            result = result.filter { $0.type == .course }
        }
        
        if showUnreadOnly {
            result = result.filter { !$0.isRead }
        }
        
        return result
    }
}

struct NotificationFilterView: View {
    @Binding var selectedType: NotificationFilterType
    @Binding var showUnreadOnly: Bool
    let unreadCount: Int
    
    var body: some View {
        ScrollView(.horizontal, showsIndicators: false) {
            HStack(spacing: 12) {
                ForEach(NotificationFilterType.allCases, id: \.self) { type in
                    FilterChip(
                        title: type.title,
                        isSelected: selectedType == type,
                        count: type == .all ? unreadCount : nil
                    ) {
                        selectedType = type
                    }
                }
                
                Toggle("仅未读", isOn: $showUnreadOnly)
                    .toggleStyle(.button)
                    .tint(Color(hex: "1890FF"))
                    .font(.caption)
                    .padding(.horizontal, 12)
                    .padding(.vertical, 6)
                    .background(showUnreadOnly ? Color(hex: "E6F7FF") : Color(hex: "F5F5F5"))
                    .cornerRadius(16)
            }
            .padding(.horizontal, 4)
        }
    }
}

struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let count: Int?
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack(spacing: 4) {
                Text(title)
                    .font(.subheadline)
                
                if let count = count, count > 0 {
                    Text("\(count)")
                        .font(.caption2)
                        .padding(.horizontal, 6)
                        .padding(.vertical, 2)
                        .background(Color.red)
                        .foregroundColor(.white)
                        .cornerRadius(10)
                }
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)
            .background(isSelected ? Color(hex: "1890FF") : Color.white)
            .foregroundColor(isSelected ? .white : .primary)
            .cornerRadius(20)
        }
    }
}

struct NotificationCardView: View {
    let notification: NotificationModel
    
    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            NotificationIconView(type: notification.type)
            
            VStack(alignment: .leading, spacing: 6) {
                HStack {
                    Text(notification.title)
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.primary)
                    
                    Spacer()
                    
                    if !notification.isRead {
                        Circle()
                            .fill(Color.red)
                            .frame(width: 8, height: 8)
                    }
                }
                
                Text(notification.content)
                    .font(.caption)
                    .foregroundColor(.secondary)
                    .lineLimit(2)
                
                HStack {
                    Text(notification.time)
                        .font(.caption2)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    if notification.isActionable {
                        Text("查看详情")
                            .font(.caption)
                            .foregroundColor(Color(hex: "1890FF"))
                    }
                }
            }
        }
        .padding()
        .background(notification.isRead ? Color.white : Color(hex: "F0F7FF"))
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.03), radius: 3, x: 0, y: 1)
    }
}

struct NotificationIconView: View {
    let type: NotificationType
    
    var body: some View {
        ZStack {
            Circle()
                .fill(iconBackgroundColor)
                .frame(width: 40, height: 40)
            
            Image(systemName: iconName)
                .foregroundColor(iconColor)
                .font(.system(size: 16))
        }
    }
    
    var iconName: String {
        switch type {
        case .homework: return "doc.text"
        case .grade: return "chart.bar"
        case .system: return "bell"
        case .course: return "book"
        }
    }
    
    var iconColor: Color {
        switch type {
        case .homework: return Color(hex: "1890FF")
        case .grade: return Color(hex: "52C41A")
        case .system: return Color(hex: "FA8C16")
        case .course: return Color(hex: "722ED1")
        }
    }
    
    var iconBackgroundColor: Color {
        switch type {
        case .homework: return Color(hex: "E6F7FF")
        case .grade: return Color(hex: "F6FFED")
        case .system: return Color(hex: "FFF7E6")
        case .course: return Color(hex: "F9F0FF")
        }
    }
}

enum NotificationFilterType: CaseIterable {
    case all, homework, grade, system, course
    
    var title: String {
        switch self {
        case .all: return "全部"
        case .homework: return "作业"
        case .grade: return "成绩"
        case .system: return "系统"
        case .course: return "课程"
        }
    }
}

@MainActor
class NotificationViewModel: ObservableObject {
    @Published var notifications: [NotificationModel] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    var unreadCount: Int {
        notifications.filter { !$0.isRead }.count
    }
    
    func loadNotifications() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            notifications = try await APIClient.shared.getNotifications()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    func markAsRead(_ notificationId: String) {
        if let index = notifications.firstIndex(where: { $0.id == notificationId }) {
            notifications[index].isRead = true
        }
        
        Task {
            try? await APIClient.shared.markNotificationAsRead(notificationId)
        }
    }
    
    func markAllAsRead() {
        for index in notifications.indices {
            notifications[index].isRead = true
        }
        
        Task {
            try? await APIClient.shared.markAllNotificationsAsRead()
        }
    }
    
    func clearReadNotifications() {
        notifications.removeAll { $0.isRead }
        
        Task {
            try? await APIClient.shared.clearReadNotifications()
        }
    }
}
