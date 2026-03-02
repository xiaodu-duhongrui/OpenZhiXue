import SwiftUI

struct ScheduleView: View {
    @StateObject private var viewModel = ScheduleViewModel()
    @State private var selectedWeek = Date()
    @State private var showDatePicker = false
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(hex: "F5F7FA")
                    .ignoresSafeArea()
                
                if viewModel.isLoading {
                    ProgressView("加载中...")
                } else {
                    VStack(spacing: 0) {
                        WeekSelectorView(selectedWeek: $selectedWeek, onPrevious: {
                            selectedWeek = Calendar.current.date(byAdding: .weekOfYear, value: -1, to: selectedWeek) ?? selectedWeek
                        }, onNext: {
                            selectedWeek = Calendar.current.date(byAdding: .weekOfYear, value: 1, to: selectedWeek) ?? selectedWeek
                        })
                        
                        WeekdayHeaderView(selectedDate: selectedWeek)
                        
                        ScrollView {
                            ScheduleGridView(
                                schedule: viewModel.schedule,
                                selectedDate: selectedWeek
                            )
                            .padding()
                        }
                    }
                }
            }
            .navigationTitle("课程表")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showDatePicker = true }) {
                        Image(systemName: "calendar")
                    }
                }
            }
            .sheet(isPresented: $showDatePicker) {
                DatePickerSheet(selectedDate: $selectedWeek)
            }
        }
        .task {
            await viewModel.loadSchedule(weekStart: selectedWeek)
        }
        .onChange(of: selectedWeek) { _, newWeek in
            Task {
                await viewModel.loadSchedule(weekStart: newWeek)
            }
        }
    }
}

struct WeekSelectorView: View {
    @Binding var selectedWeek: Date
    let onPrevious: () -> Void
    let onNext: () -> Void
    
    var body: some View {
        HStack {
            Button(action: onPrevious) {
                Image(systemName: "chevron.left")
                    .foregroundColor(.primary)
            }
            
            Spacer()
            
            VStack(spacing: 2) {
                Text(formatWeekRange(selectedWeek))
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Text("第\(weekNumber(selectedWeek))周")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            Button(action: onNext) {
                Image(systemName: "chevron.right")
                    .foregroundColor(.primary)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 12)
        .background(Color.white)
    }
    
    private func formatWeekRange(_ date: Date) -> String {
        let calendar = Calendar.current
        let startOfWeek = calendar.date(from: calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: date)) ?? date
        let endOfWeek = calendar.date(byAdding: .day, value: 6, to: startOfWeek) ?? date
        
        let formatter = DateFormatter()
        formatter.dateFormat = "M.d"
        
        return "\(formatter.string(from: startOfWeek)) - \(formatter.string(from: endOfWeek))"
    }
    
    private func weekNumber(_ date: Date) -> Int {
        let calendar = Calendar.current
        return calendar.component(.weekOfYear, from: date)
    }
}

struct WeekdayHeaderView: View {
    let selectedDate: Date
    
    private let weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    
    var body: some View {
        HStack(spacing: 0) {
            ForEach(0..<7, id: \.self) { index in
                VStack(spacing: 4) {
                    Text(weekdays[index])
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Text(dayNumber(index))
                        .font(.subheadline)
                        .fontWeight(isToday(index) ? .bold : .regular)
                        .foregroundColor(isToday(index) ? .white : .primary)
                        .frame(width: 28, height: 28)
                        .background(isToday(index) ? Color(hex: "1890FF") : Color.clear)
                        .cornerRadius(14)
                }
                .frame(maxWidth: .infinity)
            }
        }
        .padding(.vertical, 12)
        .background(Color.white)
    }
    
    private func dayNumber(_ index: Int) -> String {
        let calendar = Calendar.current
        let startOfWeek = calendar.date(from: calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: selectedDate)) ?? selectedDate
        let targetDate = calendar.date(byAdding: .day, value: index, to: startOfWeek) ?? selectedDate
        return "\(calendar.component(.day, from: targetDate))"
    }
    
    private func isToday(_ index: Int) -> Bool {
        let calendar = Calendar.current
        let startOfWeek = calendar.date(from: calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: selectedDate)) ?? selectedDate
        let targetDate = calendar.date(byAdding: .day, value: index, to: startOfWeek) ?? selectedDate
        return calendar.isDateInToday(targetDate)
    }
}

struct ScheduleGridView: View {
    let schedule: WeeklyScheduleModel
    let selectedDate: Date
    
    private let timeSlots = [
        "第1节\n8:00",
        "第2节\n8:55",
        "第3节\n9:50",
        "第4节\n10:45",
        "第5节\n14:00",
        "第6节\n14:55",
        "第7节\n15:50",
        "第8节\n16:45"
    ]
    
    var body: some View {
        HStack(alignment: .top, spacing: 4) {
            VStack(spacing: 4) {
                Color.clear
                    .frame(height: 20)
                
                ForEach(0..<timeSlots.count, id: \.self) { index in
                    Text(timeSlots[index])
                        .font(.caption2)
                        .foregroundColor(.secondary)
                        .frame(height: 70)
                }
            }
            .frame(width: 45)
            
            ForEach(0..<7, id: \.self) { dayIndex in
                VStack(spacing: 4) {
                    ForEach(0..<timeSlots.count, id: \.self) { slotIndex in
                        if let course = schedule.getCourse(day: dayIndex, slot: slotIndex) {
                            CourseCellView(course: course)
                        } else {
                            Color.clear
                                .frame(height: 70)
                        }
                    }
                }
                .frame(maxWidth: .infinity)
            }
        }
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct CourseCellView: View {
    let course: ScheduleCourseModel
    
    var body: some View {
        VStack(spacing: 4) {
            Text(course.name)
                .font(.caption2)
                .fontWeight(.medium)
                .lineLimit(2)
                .multilineTextAlignment(.center)
            
            if !course.teacher.isEmpty {
                Text(course.teacher)
                    .font(.system(size: 9))
                    .foregroundColor(.white.opacity(0.8))
            }
            
            if !course.room.isEmpty {
                Text(course.room)
                    .font(.system(size: 9))
                    .foregroundColor(.white.opacity(0.8))
            }
        }
        .padding(4)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(courseColor)
        .cornerRadius(6)
        .frame(height: 70)
    }
    
    private var courseColor: Color {
        let colors = [
            Color(hex: "1890FF"),
            Color(hex: "52C41A"),
            Color(hex: "722ED1"),
            Color(hex: "FA8C16"),
            Color(hex: "13C2C2"),
            Color(hex: "EB2F96"),
            Color(hex: "FAAD14"),
            Color(hex: "2F54EB")
        ]
        
        let hash = course.name.hashValue
        return colors[abs(hash) % colors.count]
    }
}

struct DatePickerSheet: View {
    @Binding var selectedDate: Date
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            DatePicker(
                "选择日期",
                selection: $selectedDate,
                displayedComponents: .date
            )
            .datePickerStyle(.graphical)
            .padding()
            .navigationTitle("选择日期")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("确定") {
                        dismiss()
                    }
                }
            }
        }
        .presentationDetents([.medium])
    }
}

@MainActor
class ScheduleViewModel: ObservableObject {
    @Published var schedule: WeeklyScheduleModel = WeeklyScheduleModel(courses: [:])
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func loadSchedule(weekStart: Date) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            let calendar = Calendar.current
            let startOfWeek = calendar.date(from: calendar.dateComponents([.yearForWeekOfYear, .weekOfYear], from: weekStart)) ?? weekStart
            
            schedule = try await APIClient.shared.getSchedule(weekStart: startOfWeek)
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
