import SwiftUI

struct GradeListView: View {
    @StateObject private var viewModel = GradeViewModel()
    @State private var selectedSemester: String = "全部"
    @State private var showFilterSheet = false
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(hex: "F5F7FA")
                    .ignoresSafeArea()
                
                if viewModel.isLoading {
                    ProgressView("加载中...")
                } else if viewModel.grades.isEmpty {
                    EmptyStateView(
                        icon: "chart.bar.fill",
                        title: "暂无成绩数据",
                        subtitle: "完成作业后可查看成绩"
                    )
                } else {
                    ScrollView {
                        LazyVStack(spacing: 12) {
                            ForEach(viewModel.filteredGrades(selectedSemester: selectedSemester)) { grade in
                                NavigationLink(destination: GradeDetailView(grade: grade)) {
                                    GradeCardView(grade: grade)
                                }
                                .buttonStyle(PlainButtonStyle())
                            }
                        }
                        .padding()
                    }
                    .refreshable {
                        await viewModel.loadGrades()
                    }
                }
            }
            .navigationTitle("成绩查询")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showFilterSheet = true }) {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                    }
                }
            }
            .sheet(isPresented: $showFilterSheet) {
                SemesterFilterSheet(
                    selectedSemester: $selectedSemester,
                    semesters: viewModel.semesters
                )
            }
        }
        .task {
            await viewModel.loadGrades()
        }
    }
}

struct GradeCardView: View {
    let grade: GradeModel
    
    var body: some View {
        HStack(spacing: 16) {
            VStack(alignment: .leading, spacing: 8) {
                Text(grade.examName)
                    .font(.headline)
                    .foregroundColor(.primary)
                
                Text(grade.subject)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                
                Text(grade.date)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                Text(String(format: "%.1f", grade.score))
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(gradeColor(score: grade.score, total: grade.totalScore))
                
                Text("/\(grade.totalScore, specifier: "%.0f")")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Text("排名: \(grade.rank)/\(grade.totalStudents)")
                    .font(.caption2)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)
    }
    
    private func gradeColor(score: Double, total: Double) -> Color {
        let percentage = score / total
        if percentage >= 0.9 { return Color(hex: "52C41A") }
        if percentage >= 0.8 { return Color(hex: "1890FF") }
        if percentage >= 0.7 { return Color(hex: "FAAD14") }
        if percentage >= 0.6 { return Color(hex: "FA8C16") }
        return Color(hex: "F5222D")
    }
}

struct GradeDetailView: View {
    let grade: GradeModel
    @StateObject private var viewModel = GradeDetailViewModel()
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                ScoreHeaderView(grade: grade)
                
                if let detail = viewModel.detail {
                    ScoreAnalysisView(detail: detail)
                    
                    if !detail.questions.isEmpty {
                        QuestionAnalysisView(questions: detail.questions)
                    }
                    
                    if !detail.rankDistribution.isEmpty {
                        RankDistributionView(distribution: detail.rankDistribution)
                    }
                }
            }
            .padding()
        }
        .navigationTitle(grade.subject)
        .navigationBarTitleDisplayMode(.inline)
        .task {
            await viewModel.loadDetail(gradeId: grade.id)
        }
    }
}

struct ScoreHeaderView: View {
    let grade: GradeModel
    
    var body: some View {
        VStack(spacing: 12) {
            Text(grade.examName)
                .font(.headline)
                .foregroundColor(.secondary)
            
            ZStack {
                Circle()
                    .stroke(Color(hex: "E8E8E8"), lineWidth: 12)
                    .frame(width: 120, height: 120)
                
                Circle()
                    .trim(from: 0, to: grade.score / grade.totalScore)
                    .stroke(
                        scoreColor,
                        style: StrokeStyle(lineWidth: 12, lineCap: .round)
                    )
                    .frame(width: 120, height: 120)
                    .rotationEffect(.degrees(-90))
                
                VStack(spacing: 4) {
                    Text(String(format: "%.1f", grade.score))
                        .font(.title)
                        .fontWeight(.bold)
                        .foregroundColor(scoreColor)
                    
                    Text("总分 \(grade.totalScore, specifier: "%.0f")")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            HStack(spacing: 32) {
                VStack {
                    Text("\(grade.rank)")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                    Text("班级排名")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                VStack {
                    Text("\(grade.totalStudents)")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                    Text("参考人数")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                VStack {
                    Text(String(format: "%.1f%%", grade.score / grade.totalScore * 100))
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.primary)
                    Text("得分率")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
    
    private var scoreColor: Color {
        let percentage = grade.score / grade.totalScore
        if percentage >= 0.9 { return Color(hex: "52C41A") }
        if percentage >= 0.8 { return Color(hex: "1890FF") }
        if percentage >= 0.7 { return Color(hex: "FAAD14") }
        return Color(hex: "FA8C16")
    }
}

struct ScoreAnalysisView: View {
    let detail: GradeDetailModel
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("成绩分析")
                .font(.headline)
            
            HStack {
                VStack(alignment: .leading, spacing: 8) {
                    AnalysisRow(label: "班级平均分", value: String(format: "%.1f", detail.classAverage))
                    AnalysisRow(label: "班级最高分", value: String(format: "%.1f", detail.classHighest))
                    AnalysisRow(label: "班级最低分", value: String(format: "%.1f", detail.classLowest))
                }
                
                Spacer()
                
                VStack(alignment: .leading, spacing: 8) {
                    AnalysisRow(label: "年级平均分", value: String(format: "%.1f", detail.gradeAverage))
                    AnalysisRow(label: "年级最高分", value: String(format: "%.1f", detail.gradeHighest))
                    AnalysisRow(label: "年级最低分", value: String(format: "%.1f", detail.gradeLowest))
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct AnalysisRow: View {
    let label: String
    let value: String
    
    var body: some View {
        HStack {
            Text(label)
                .font(.subheadline)
                .foregroundColor(.secondary)
            Spacer()
            Text(value)
                .font(.subheadline)
                .fontWeight(.medium)
        }
    }
}

struct QuestionAnalysisView: View {
    let questions: [QuestionScoreModel]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("题目得分")
                .font(.headline)
            
            LazyVGrid(columns: Array(repeating: GridItem(.flexible()), count: 5), spacing: 12) {
                ForEach(questions) { question in
                    QuestionScoreCell(question: question)
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct QuestionScoreCell: View {
    let question: QuestionScoreModel
    
    var body: some View {
        VStack(spacing: 4) {
            Text("第\(question.number)题")
                .font(.caption2)
                .foregroundColor(.secondary)
            
            Text(String(format: "%.1f", question.score))
                .font(.caption)
                .fontWeight(.medium)
                .foregroundColor(question.score >= question.maxScore ? .green : (question.score > 0 ? .orange : .red))
            
            Text("/\(question.maxScore, specifier: "%.0f")")
                .font(.caption2)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
        .padding(.vertical, 8)
        .background(question.score >= question.maxScore ? Color.green.opacity(0.1) : (question.score > 0 ? Color.orange.opacity(0.1) : Color.red.opacity(0.1)))
        .cornerRadius(8)
    }
}

struct RankDistributionView: View {
    let distribution: [RankDistributionModel]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("分数段分布")
                .font(.headline)
            
            ForEach(distribution) { segment in
                HStack {
                    Text(segment.range)
                        .font(.subheadline)
                        .frame(width: 80, alignment: .leading)
                    
                    GeometryReader { geometry in
                        ZStack(alignment: .leading) {
                            RoundedRectangle(cornerRadius: 4)
                                .fill(Color(hex: "E8E8E8"))
                                .frame(height: 20)
                            
                            RoundedRectangle(cornerRadius: 4)
                                .fill(Color(hex: "1890FF"))
                                .frame(width: geometry.size.width * CGFloat(segment.percentage) / 100, height: 20)
                        }
                    }
                    .frame(height: 20)
                    
                    Text("\(segment.count)人")
                        .font(.caption)
                        .foregroundColor(.secondary)
                        .frame(width: 50, alignment: .trailing)
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct SemesterFilterSheet: View {
    @Binding var selectedSemester: String
    let semesters: [String]
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            List {
                Button(action: {
                    selectedSemester = "全部"
                    dismiss()
                }) {
                    HStack {
                        Text("全部")
                        Spacer()
                        if selectedSemester == "全部" {
                            Image(systemName: "checkmark")
                                .foregroundColor(.blue)
                        }
                    }
                }
                
                ForEach(semesters, id: \.self) { semester in
                    Button(action: {
                        selectedSemester = semester
                        dismiss()
                    }) {
                        HStack {
                            Text(semester)
                            Spacer()
                            if selectedSemester == semester {
                                Image(systemName: "checkmark")
                                .foregroundColor(.blue)
                            }
                        }
                    }
                }
            }
            .navigationTitle("选择学期")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("取消") {
                        dismiss()
                    }
                }
            }
        }
        .presentationDetents([.medium])
    }
}

@MainActor
class GradeViewModel: ObservableObject {
    @Published var grades: [GradeModel] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    var semesters: [String] {
        Array(Set(grades.map { $0.semester })).sorted(by: >)
    }
    
    func loadGrades() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            grades = try await APIClient.shared.getGrades()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    func filteredGrades(selectedSemester: String) -> [GradeModel] {
        if selectedSemester == "全部" {
            return grades
        }
        return grades.filter { $0.semester == selectedSemester }
    }
}

@MainActor
class GradeDetailViewModel: ObservableObject {
    @Published var detail: GradeDetailModel?
    @Published var isLoading = false
    
    func loadDetail(gradeId: String) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            detail = try await APIClient.shared.getGradeDetail(gradeId: gradeId)
        } catch {
            print("Error loading grade detail: \(error)")
        }
    }
}
