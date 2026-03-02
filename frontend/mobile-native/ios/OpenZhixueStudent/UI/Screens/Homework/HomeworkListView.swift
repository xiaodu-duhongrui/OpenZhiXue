import SwiftUI

struct HomeworkListView: View {
    @StateObject private var viewModel = HomeworkListViewModel()
    
    var body: some View {
        NavigationView {
            VStack {
                if viewModel.isLoading {
                    LoadingView()
                } else if let error = viewModel.error {
                    ErrorStateView(message: error, retryAction: { viewModel.loadData() })
                } else if viewModel.homeworks.isEmpty {
                    EmptyStateView(icon: "doc.text", message: "暂无作业")
                } else {
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(viewModel.homeworks) { homework in
                                HomeworkListItemView(homework: homework)
                                    .onTapGesture {
                                        viewModel.selectedHomework = homework
                                    }
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("作业列表")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button("全部", action: { viewModel.filterByStatus(nil) })
                        Button("待完成", action: { viewModel.filterByStatus(.pending) })
                        Button("已提交", action: { viewModel.filterByStatus(.submitted) })
                        Button("已批改", action: { viewModel.filterByStatus(.graded) })
                    } label: {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                    }
                }
            }
        }
    }
}

struct HomeworkListItemView: View {
    let homework: Homework
    
    var body: some View {
        CardView {
            HStack {
                VStack(alignment: .leading, spacing: 6) {
                    Text(homework.title)
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    
                    Text("\(homework.courseName) · \(homework.teacherName)")
                        .font(.subheadline)
                        .foregroundColor(.textSecondary)
                    
                    Text("截止: \(formatDate(homework.endTime))")
                        .font(.caption)
                        .foregroundColor(.textHint)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 6) {
                    StatusBadge(text: statusText, color: statusColor)
                    
                    if let score = homework.score {
                        Text("\(score)分")
                            .font(.headline)
                            .foregroundColor(.success)
                    }
                }
            }
        }
    }
    
    var statusText: String {
        switch homework.status {
        case .pending: return "待完成"
        case .submitted: return "已提交"
        case .graded: return "已批改"
        case .late: return "已逾期"
        }
    }
    
    var statusColor: Color {
        switch homework.status {
        case .pending: return .warning
        case .submitted: return .info
        case .graded: return .success
        case .late: return .error
        }
    }
    
    private func formatDate(_ dateString: String) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ss"
        guard let date = formatter.date(from: dateString) else { return dateString }
        
        let displayFormatter = DateFormatter()
        displayFormatter.dateFormat = "MM-dd HH:mm"
        return displayFormatter.string(from: date)
    }
}

class HomeworkListViewModel: ObservableObject {
    @Published var homeworks: [Homework] = []
    @Published var isLoading: Bool = false
    @Published var error: String?
    @Published var selectedHomework: Homework?
    @Published var selectedStatus: HomeworkStatus?
    
    func loadData() {
        isLoading = true
        error = nil
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.homeworks = [
                Homework(
                    id: "1",
                    title: "数学作业第三章习题",
                    description: "完成课本第三章所有习题",
                    courseId: "math",
                    courseName: "数学",
                    teacherId: "t1",
                    teacherName: "王老师",
                    endTime: "2024-01-15T18:00:00",
                    status: .pending,
                    score: nil,
                    feedback: nil,
                    attachments: [],
                    submittedAt: nil
                ),
                Homework(
                    id: "2",
                    title: "英语阅读理解练习",
                    description: "完成阅读理解练习册第10页",
                    courseId: "english",
                    courseName: "英语",
                    teacherId: "t2",
                    teacherName: "李老师",
                    endTime: "2024-01-14T18:00:00",
                    status: .submitted,
                    score: nil,
                    feedback: nil,
                    attachments: [],
                    submittedAt: "2024-01-13T15:00:00"
                ),
                Homework(
                    id: "3",
                    title: "物理实验报告",
                    description: "提交上周实验的报告",
                    courseId: "physics",
                    courseName: "物理",
                    teacherId: "t3",
                    teacherName: "张老师",
                    endTime: "2024-01-12T18:00:00",
                    status: .graded,
                    score: 95,
                    feedback: "实验报告完成得很好",
                    attachments: [],
                    submittedAt: "2024-01-11T10:00:00"
                )
            ]
            self.isLoading = false
        }
    }
    
    func filterByStatus(_ status: HomeworkStatus?) {
        selectedStatus = status
        loadData()
    }
}

struct HomeworkListView_Previews: PreviewProvider {
    static var previews: some View {
        HomeworkListView()
    }
}
