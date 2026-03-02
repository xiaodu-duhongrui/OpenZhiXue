import SwiftUI

struct CourseListView: View {
    @StateObject private var viewModel = CourseListViewModel()
    
    var body: some View {
        NavigationView {
            VStack {
                if viewModel.isLoading {
                    LoadingView()
                } else if viewModel.courses.isEmpty {
                    EmptyStateView(icon: "book", message: "暂无课程")
                } else {
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(viewModel.courses) { course in
                                CourseListItemView(course: course)
                            }
                        }
                        .padding()
                    }
                }
            }
            .navigationTitle("我的课程")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    NavigationLink(destination: ScheduleView()) {
                        Image(systemName: "calendar")
                    }
                }
            }
        }
    }
}

struct CourseListItemView: View {
    let course: Course
    
    var body: some View {
        CardView {
            HStack(spacing: 16) {
                ZStack {
                    Circle()
                        .fill(courseColor.opacity(0.1))
                        .frame(width: 56, height: 56)
                    
                    Image(systemName: "book.fill")
                        .font(.title2)
                        .foregroundColor(courseColor)
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(course.name)
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    
                    Text("\(course.teacherName) · \(course.credit)学分")
                        .font(.subheadline)
                        .foregroundColor(.textSecondary)
                }
                
                Spacer()
                
                if course.studentCount > 0 {
                    Text("\(course.studentCount)人")
                        .font(.caption)
                        .foregroundColor(.textHint)
                }
            }
        }
    }
    
    var courseColor: Color {
        let colors: [Color] = [.info, .success, .warning, .purple, .orange, .pink]
        let hash = abs(course.id.hashValue)
        return colors[hash % colors.count]
    }
}

struct ScheduleView: View {
    @State private var currentWeek: Int = 1
    @State private var totalWeeks: Int = 20
    
    let weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    let periods = [1, 2, 3, 4, 5, 6, 7, 8]
    
    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Button(action: { if currentWeek > 1 { currentWeek -= 1 } }) {
                    Image(systemName: "chevron.left")
                }
                .disabled(currentWeek <= 1)
                
                Spacer()
                
                Text("第 \(currentWeek) 周")
                    .font(.headline)
                
                Spacer()
                
                Button(action: { if currentWeek < totalWeeks { currentWeek += 1 } }) {
                    Image(systemName: "chevron.right")
                }
                .disabled(currentWeek >= totalWeeks)
            }
            .padding()
            
            Divider()
            
            ScrollView {
                VStack(spacing: 0) {
                    HStack(spacing: 0) {
                        Text("节次")
                            .font(.caption)
                            .frame(width: 40)
                        
                        ForEach(weekdays, id: \.self) { day in
                            Text(day)
                                .font(.caption)
                                .frame(maxWidth: .infinity)
                        }
                    }
                    .padding(.vertical, 8)
                    .background(Color.surfaceColor)
                    
                    ForEach(periods, id: \.self) { period in
                        HStack(spacing: 0) {
                            Text("\(period)")
                                .font(.caption)
                                .frame(width: 40)
                            
                            ForEach(1...7, id: \.self) { weekday in
                                ScheduleCell(weekday: weekday, period: period)
                            }
                        }
                        .frame(height: 50)
                    }
                }
            }
        }
        .navigationTitle("课程表")
        .navigationBarTitleDisplayMode(.inline)
    }
}

struct ScheduleCell: View {
    let weekday: Int
    let period: Int
    
    var body: some View {
        Rectangle()
            .fill(Color.clear)
            .frame(maxWidth: .infinity)
            .overlay(
                Rectangle()
                    .stroke(Color.textHint.opacity(0.2), lineWidth: 0.5)
            )
    }
}

class CourseListViewModel: ObservableObject {
    @Published var courses: [Course] = []
    @Published var isLoading: Bool = false
    
    init() {
        loadData()
    }
    
    func loadData() {
        isLoading = true
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.5) {
            self.courses = [
                Course(
                    id: "1",
                    name: "高等数学",
                    code: "MATH101",
                    teacherId: "t1",
                    teacherName: "王老师",
                    credit: 4,
                    description: "高等数学课程",
                    academicYear: "2023-2024",
                    semester: 1,
                    studentCount: 45
                ),
                Course(
                    id: "2",
                    name: "大学英语",
                    code: "ENG101",
                    teacherId: "t2",
                    teacherName: "李老师",
                    credit: 3,
                    description: "大学英语课程",
                    academicYear: "2023-2024",
                    semester: 1,
                    studentCount: 42
                ),
                Course(
                    id: "3",
                    name: "大学物理",
                    code: "PHY101",
                    teacherId: "t3",
                    teacherName: "张老师",
                    credit: 3,
                    description: "大学物理课程",
                    academicYear: "2023-2024",
                    semester: 1,
                    studentCount: 48
                )
            ]
            self.isLoading = false
        }
    }
}

struct CourseListView_Previews: PreviewProvider {
    static var previews: some View {
        CourseListView()
    }
}
