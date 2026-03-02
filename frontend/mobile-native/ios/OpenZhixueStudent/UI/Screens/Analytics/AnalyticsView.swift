import SwiftUI
import Charts

struct AnalyticsView: View {
    @StateObject private var viewModel = AnalyticsViewModel()
    @State private var selectedPeriod: AnalyticsPeriod = .semester
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(hex: "F5F7FA")
                    .ignoresSafeArea()
                
                if viewModel.isLoading {
                    ProgressView("加载中...")
                } else {
                    ScrollView {
                        VStack(spacing: 16) {
                            PeriodPickerView(selectedPeriod: $selectedPeriod)
                            
                            if let overview = viewModel.overview {
                                AnalyticsOverviewCard(overview: overview)
                            }
                            
                            if let subjectAnalysis = viewModel.subjectAnalysis {
                                SubjectRadarChartView(data: subjectAnalysis)
                            }
                            
                            if let trendData = viewModel.trendData {
                                ScoreTrendChartView(data: trendData)
                            }
                            
                            if let rankTrend = viewModel.rankTrend {
                                RankTrendChartView(data: rankTrend)
                            }
                            
                            if !viewModel.subjectDetails.isEmpty {
                                SubjectDetailsView(details: viewModel.subjectDetails)
                            }
                            
                            if let suggestions = viewModel.suggestions, !suggestions.isEmpty {
                                StudySuggestionsView(suggestions: suggestions)
                            }
                        }
                        .padding()
                    }
                    .refreshable {
                        await viewModel.loadAnalytics(period: selectedPeriod)
                    }
                }
            }
            .navigationTitle("学情分析")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { viewModel.exportReport() }) {
                        Image(systemName: "square.and.arrow.up")
                    }
                }
            }
        }
        .task {
            await viewModel.loadAnalytics(period: selectedPeriod)
        }
        .onChange(of: selectedPeriod) { _, newPeriod in
            Task {
                await viewModel.loadAnalytics(period: newPeriod)
            }
        }
    }
}

struct PeriodPickerView: View {
    @Binding var selectedPeriod: AnalyticsPeriod
    
    var body: some View {
        HStack(spacing: 0) {
            ForEach(AnalyticsPeriod.allCases, id: \.self) { period in
                Button(action: { selectedPeriod = period }) {
                    Text(period.title)
                        .font(.subheadline)
                        .fontWeight(selectedPeriod == period ? .semibold : .regular)
                        .foregroundColor(selectedPeriod == period ? .white : .primary)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 10)
                        .background(selectedPeriod == period ? Color(hex: "1890FF") : Color.clear)
                }
            }
        }
        .background(Color(hex: "F0F0F0"))
        .cornerRadius(8)
    }
}

struct AnalyticsOverviewCard: View {
    let overview: AnalyticsOverviewModel
    
    var body: some View {
        VStack(spacing: 16) {
            Text("学习概览")
                .font(.headline)
                .frame(maxWidth: .infinity, alignment: .leading)
            
            HStack(spacing: 16) {
                OverviewItem(title: "平均分", value: String(format: "%.1f", overview.averageScore), color: Color(hex: "1890FF"))
                OverviewItem(title: "排名", value: "\(overview.rank)", color: Color(hex: "52C41A"))
                OverviewItem(title: "进步", value: overview.progress >= 0 ? "+\(overview.progress)" : "\(overview.progress)", color: overview.progress >= 0 ? .green : .red)
            }
            
            HStack(spacing: 16) {
                OverviewItem(title: "作业完成", value: "\(overview.homeworkCompletion)%", color: Color(hex: "722ED1"))
                OverviewItem(title: "错题数", value: "\(overview.mistakeCount)", color: Color(hex: "FA8C16"))
                OverviewItem(title: "学习天数", value: "\(overview.studyDays)", color: Color(hex: "13C2C2"))
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct OverviewItem: View {
    let title: String
    let value: String
    let color: Color
    
    var body: some View {
        VStack(spacing: 8) {
            Text(value)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(color)
            
            Text(title)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .frame(maxWidth: .infinity)
    }
}

struct SubjectRadarChartView: View {
    let data: [SubjectAnalysisModel]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("学科能力分析")
                .font(.headline)
            
            Chart(data) { item in
                RadarChartMark(
                    key: item.subject,
                    value: item.score
                )
                .foregroundStyle(Color(hex: "1890FF").opacity(0.3))
                .symbol(by: item.subject)
            }
            .chartRadarChart { _ in
                ChartRadarChart()
                    .levels(5)
                    .foregroundStyle(Color.gray.opacity(0.2))
            }
            .frame(height: 250)
            
            HStack {
                ForEach(data.prefix(4)) { item in
                    VStack {
                        Circle()
                            .fill(Color(hex: "1890FF"))
                            .frame(width: 8, height: 8)
                        Text(item.subject)
                            .font(.caption2)
                            .foregroundColor(.secondary)
                    }
                    .frame(maxWidth: .infinity)
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct ScoreTrendChartView: View {
    let data: [TrendDataModel]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("成绩趋势")
                .font(.headline)
            
            Chart(data) { item in
                LineMark(
                    x: .value("时间", item.date),
                    y: .value("分数", item.score)
                )
                .foregroundStyle(Color(hex: "1890FF"))
                .symbol(by: item.date)
                
                AreaMark(
                    x: .value("时间", item.date),
                    y: .value("分数", item.score)
                )
                .foregroundStyle(
                    .linearGradient(
                        colors: [Color(hex: "1890FF").opacity(0.3), Color(hex: "1890FF").opacity(0.05)],
                        startPoint: .top,
                        endPoint: .bottom
                    )
                )
            }
            .chartYAxis {
                AxisMarks(position: .leading)
            }
            .chartXAxis {
                AxisMarks(values: .automatic(desiredCount: 5))
            }
            .frame(height: 200)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct RankTrendChartView: View {
    let data: [RankTrendModel]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("排名趋势")
                .font(.headline)
            
            Chart(data) { item in
                BarMark(
                    x: .value("时间", item.date),
                    y: .value("排名", item.rank)
                )
                .foregroundStyle(Color(hex: "52C41A"))
            }
            .chartYAxis {
                AxisMarks(position: .leading)
            }
            .chartYScale(domain: .automatic(reversed: true))
            .frame(height: 200)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct SubjectDetailsView: View {
    let details: [SubjectDetailModel]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("学科详情")
                .font(.headline)
            
            ForEach(details) { detail in
                SubjectDetailRow(detail: detail)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct SubjectDetailRow: View {
    let detail: SubjectDetailModel
    
    var body: some View {
        VStack(spacing: 8) {
            HStack {
                Text(detail.subject)
                    .font(.subheadline)
                    .fontWeight(.medium)
                
                Spacer()
                
                Text(String(format: "%.1f", detail.averageScore))
                    .font(.subheadline)
                    .fontWeight(.semibold)
                    .foregroundColor(scoreColor)
            }
            
            GeometryReader { geometry in
                ZStack(alignment: .leading) {
                    RoundedRectangle(cornerRadius: 4)
                        .fill(Color(hex: "E8E8E8"))
                        .frame(height: 8)
                    
                    RoundedRectangle(cornerRadius: 4)
                        .fill(scoreColor)
                        .frame(width: geometry.size.width * CGFloat(detail.averageScore / 100), height: 8)
                }
            }
            .frame(height: 8)
            
            HStack {
                Label("\(detail.examCount)次考试", systemImage: "doc.text")
                    .font(.caption)
                    .foregroundColor(.secondary)
                
                Spacer()
                
                Label(detail.trend >= 0 ? "进步\(detail.trend)分" : "退步\(-detail.trend)分",
                      systemImage: detail.trend >= 0 ? "arrow.up.right" : "arrow.down.right")
                    .font(.caption)
                    .foregroundColor(detail.trend >= 0 ? .green : .red)
            }
        }
        .padding(.vertical, 8)
    }
    
    private var scoreColor: Color {
        if detail.averageScore >= 90 { return Color(hex: "52C41A") }
        if detail.averageScore >= 80 { return Color(hex: "1890FF") }
        if detail.averageScore >= 70 { return Color(hex: "FAAD14") }
        if detail.averageScore >= 60 { return Color(hex: "FA8C16") }
        return Color(hex: "F5222D")
    }
}

struct StudySuggestionsView: View {
    let suggestions: [StudySuggestionModel]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("学习建议")
                    .font(.headline)
                
                Spacer()
                
                Image(systemName: "lightbulb.fill")
                    .foregroundColor(.yellow)
            }
            
            ForEach(suggestions) { suggestion in
                HStack(alignment: .top, spacing: 12) {
                    Image(systemName: suggestion.icon)
                        .foregroundColor(Color(hex: "1890FF"))
                        .frame(width: 24)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text(suggestion.title)
                            .font(.subheadline)
                            .fontWeight(.medium)
                        
                        Text(suggestion.content)
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                }
                .padding(.vertical, 4)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

enum AnalyticsPeriod: CaseIterable {
    case week, month, semester, year
    
    var title: String {
        switch self {
        case .week: return "本周"
        case .month: return "本月"
        case .semester: return "本学期"
        case .year: return "本学年"
        }
    }
}

@MainActor
class AnalyticsViewModel: ObservableObject {
    @Published var overview: AnalyticsOverviewModel?
    @Published var subjectAnalysis: [SubjectAnalysisModel] = []
    @Published var trendData: [TrendDataModel] = []
    @Published var rankTrend: [RankTrendModel] = []
    @Published var subjectDetails: [SubjectDetailModel] = []
    @Published var suggestions: [StudySuggestionModel] = []
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    func loadAnalytics(period: AnalyticsPeriod) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            async let overviewTask = APIClient.shared.getAnalyticsOverview(period: period.rawValue)
            async let subjectTask = APIClient.shared.getSubjectAnalysis(period: period.rawValue)
            async let trendTask = APIClient.shared.getScoreTrend(period: period.rawValue)
            async let rankTask = APIClient.shared.getRankTrend(period: period.rawValue)
            async let detailsTask = APIClient.shared.getSubjectDetails(period: period.rawValue)
            async let suggestionsTask = APIClient.shared.getStudySuggestions(period: period.rawValue)
            
            overview = try await overviewTask
            subjectAnalysis = try await subjectTask
            trendData = try await trendTask
            rankTrend = try await rankTask
            subjectDetails = try await detailsTask
            suggestions = try await suggestionsTask
        } catch {
            errorMessage = error.localizedDescription
        }
    }
    
    func exportReport() {
    }
}
