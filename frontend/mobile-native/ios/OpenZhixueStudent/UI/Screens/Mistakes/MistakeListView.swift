import SwiftUI

struct MistakeListView: View {
    @StateObject private var viewModel = MistakeViewModel()
    @State private var selectedSubject: String = "全部"
    @State private var selectedType: MistakeType = .all
    @State private var showFilterSheet = false
    @State private var searchText = ""
    
    var body: some View {
        NavigationView {
            ZStack {
                Color(hex: "F5F7FA")
                    .ignoresSafeArea()
                
                if viewModel.isLoading {
                    ProgressView("加载中...")
                } else if viewModel.mistakes.isEmpty {
                    EmptyStateView(
                        icon: "book.fill",
                        title: "暂无错题",
                        subtitle: "继续努力，保持优秀！"
                    )
                } else {
                    ScrollView {
                        VStack(spacing: 12) {
                            MistakeStatsView(stats: viewModel.stats)
                            
                            LazyVStack(spacing: 12) {
                                ForEach(filteredMistakes) { mistake in
                                    NavigationLink(destination: MistakeDetailView(mistake: mistake)) {
                                        MistakeCardView(mistake: mistake)
                                    }
                                    .buttonStyle(PlainButtonStyle())
                                }
                            }
                        }
                        .padding()
                    }
                    .refreshable {
                        await viewModel.loadMistakes()
                    }
                }
            }
            .navigationTitle("错题本")
            .searchable(text: $searchText, prompt: "搜索错题")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showFilterSheet = true }) {
                        Image(systemName: "line.3.horizontal.decrease.circle")
                    }
                }
            }
            .sheet(isPresented: $showFilterSheet) {
                MistakeFilterSheet(
                    selectedSubject: $selectedSubject,
                    selectedType: $selectedType,
                    subjects: viewModel.subjects
                )
            }
        }
        .task {
            await viewModel.loadMistakes()
        }
    }
    
    var filteredMistakes: [MistakeModel] {
        var result = viewModel.mistakes
        
        if selectedSubject != "全部" {
            result = result.filter { $0.subject == selectedSubject }
        }
        
        switch selectedType {
        case .all:
            break
        case .unresolved:
            result = result.filter { !$0.isResolved }
        case .resolved:
            result = result.filter { $0.isResolved }
        case .important:
            result = result.filter { $0.isImportant }
        }
        
        if !searchText.isEmpty {
            result = result.filter { 
                $0.content.localizedCaseInsensitiveContains(searchText) ||
                $0.subject.localizedCaseInsensitiveContains(searchText)
            }
        }
        
        return result
    }
}

struct MistakeStatsView: View {
    let stats: MistakeStatsModel
    
    var body: some View {
        HStack(spacing: 16) {
            StatCard(title: "总错题", value: "\(stats.total)", color: Color(hex: "1890FF"))
            StatCard(title: "未解决", value: "\(stats.unresolved)", color: Color(hex: "F5222D"))
            StatCard(title: "已解决", value: "\(stats.resolved)", color: Color(hex: "52C41A"))
            StatCard(title: "重要", value: "\(stats.important)", color: Color(hex: "FAAD14"))
        }
    }
}

struct StatCard: View {
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
        .padding(.vertical, 16)
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct MistakeCardView: View {
    let mistake: MistakeModel
    
    var body: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 8) {
                HStack {
                    Text(mistake.subject)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color(hex: "E6F7FF"))
                        .foregroundColor(Color(hex: "1890FF"))
                        .cornerRadius(4)
                    
                    if mistake.isImportant {
                        Image(systemName: "star.fill")
                            .foregroundColor(.yellow)
                            .font(.caption)
                    }
                    
                    if mistake.isResolved {
                        Text("已解决")
                            .font(.caption2)
                            .padding(.horizontal, 6)
                            .padding(.vertical, 2)
                            .background(Color.green.opacity(0.1))
                            .foregroundColor(.green)
                            .cornerRadius(4)
                    }
                    
                    Spacer()
                }
                
                Text(mistake.content)
                    .font(.subheadline)
                    .lineLimit(2)
                    .foregroundColor(.primary)
                
                HStack {
                    Text(mistake.source)
                        .font(.caption)
                        .foregroundColor(.secondary)
                    
                    Spacer()
                    
                    Text(mistake.createdAt)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            
            Image(systemName: "chevron.right")
                .foregroundColor(.secondary)
                .font(.caption)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
        .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)
    }
}

struct MistakeDetailView: View {
    let mistake: MistakeModel
    @StateObject private var viewModel = MistakeDetailViewModel()
    @State private var showResolveSheet = false
    @State private var resolveNote = ""
    
    var body: some View {
        ScrollView {
            VStack(spacing: 16) {
                MistakeHeaderView(mistake: mistake)
                
                MistakeContentView(mistake: mistake)
                
                if let analysis = viewModel.analysis {
                    MistakeAnalysisView(analysis: analysis)
                }
                
                if let similarMistakes = viewModel.similarMistakes, !similarMistakes.isEmpty {
                    SimilarMistakesView(mistakes: similarMistakes)
                }
                
                ResolveHistoryView(history: viewModel.resolveHistory)
            }
            .padding()
        }
        .navigationTitle("错题详情")
        .navigationBarTitleDisplayMode(.inline)
        .toolbar {
            ToolbarItem(placement: .navigationBarTrailing) {
                Menu {
                    Button(action: { viewModel.toggleImportant() }) {
                        Label(
                            mistake.isImportant ? "取消重要标记" : "标记为重要",
                            systemImage: mistake.isImportant ? "star.slash" : "star"
                        )
                    }
                    
                    Button(action: { showResolveSheet = true }) {
                        Label(
                            mistake.isResolved ? "取消解决" : "标记已解决",
                            systemImage: mistake.isResolved ? "xmark.circle" : "checkmark.circle"
                        )
                    }
                } label: {
                    Image(systemName: "ellipsis.circle")
                }
            }
        }
        .sheet(isPresented: $showResolveSheet) {
            ResolveMistakeSheet(note: $resolveNote) {
                viewModel.resolveMistake(note: resolveNote)
                showResolveSheet = false
            }
        }
        .task {
            await viewModel.loadDetail(mistakeId: mistake.id)
        }
    }
}

struct MistakeHeaderView: View {
    let mistake: MistakeModel
    
    var body: some View {
        HStack {
            VStack(alignment: .leading, spacing: 4) {
                Text(mistake.subject)
                    .font(.headline)
                
                Text(mistake.source)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: 4) {
                if mistake.isResolved {
                    Text("已解决")
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color.green.opacity(0.1))
                        .foregroundColor(.green)
                        .cornerRadius(4)
                }
                
                Text(mistake.createdAt)
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct MistakeContentView: View {
    let mistake: MistakeModel
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("题目内容")
                .font(.headline)
            
            Text(mistake.content)
                .font(.body)
                .foregroundColor(.primary)
            
            if !mistake.images.isEmpty {
                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(mistake.images, id: \.self) { imageUrl in
                            AsyncImage(url: URL(string: imageUrl)) { image in
                                image
                                    .resizable()
                                    .aspectRatio(contentMode: .fill)
                            } placeholder: {
                                Color.gray.opacity(0.2)
                            }
                            .frame(width: 100, height: 100)
                            .cornerRadius(8)
                        }
                    }
                }
            }
            
            Divider()
            
            Text("错误答案")
                .font(.subheadline)
                .foregroundColor(.red)
            
            Text(mistake.wrongAnswer)
                .font(.body)
                .padding()
                .background(Color.red.opacity(0.05))
                .cornerRadius(8)
            
            Text("正确答案")
                .font(.subheadline)
                .foregroundColor(.green)
            
            Text(mistake.correctAnswer)
                .font(.body)
                .padding()
                .background(Color.green.opacity(0.05))
                .cornerRadius(8)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct MistakeAnalysisView: View {
    let analysis: MistakeAnalysisModel
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("错因分析")
                .font(.headline)
            
            VStack(alignment: .leading, spacing: 8) {
                AnalysisTagRow(title: "错误类型", tags: analysis.errorTypes)
                AnalysisTagRow(title: "知识点", tags: analysis.knowledgePoints)
            }
            
            Text(analysis.analysis)
                .font(.body)
                .foregroundColor(.primary)
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct AnalysisTagRow: View {
    let title: String
    let tags: [String]
    
    var body: some View {
        HStack(alignment: .top) {
            Text(title)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .frame(width: 70, alignment: .leading)
            
            FlowLayout(spacing: 8) {
                ForEach(tags, id: \.self) { tag in
                    Text(tag)
                        .font(.caption)
                        .padding(.horizontal, 8)
                        .padding(.vertical, 4)
                        .background(Color(hex: "F0F0F0"))
                        .cornerRadius(4)
                }
            }
        }
    }
}

struct SimilarMistakesView: View {
    let mistakes: [MistakeModel]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("相似错题")
                .font(.headline)
            
            ForEach(mistakes) { mistake in
                HStack {
                    VStack(alignment: .leading, spacing: 4) {
                        Text(mistake.subject)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Text(mistake.content)
                            .font(.subheadline)
                            .lineLimit(1)
                    }
                    
                    Spacer()
                    
                    Image(systemName: "chevron.right")
                        .foregroundColor(.secondary)
                        .font(.caption)
                }
                .padding()
                .background(Color(hex: "F9F9F9"))
                .cornerRadius(8)
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct ResolveHistoryView: View {
    let history: [ResolveHistoryModel]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("解决记录")
                .font(.headline)
            
            if history.isEmpty {
                Text("暂无解决记录")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .frame(maxWidth: .infinity)
                    .padding()
            } else {
                ForEach(history) { record in
                    HStack(alignment: .top, spacing: 12) {
                        Circle()
                            .fill(Color.green)
                            .frame(width: 8, height: 8)
                            .padding(.top, 6)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(record.date)
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            if !record.note.isEmpty {
                                Text(record.note)
                                    .font(.subheadline)
                            }
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color.white)
        .cornerRadius(12)
    }
}

struct ResolveMistakeSheet: View {
    @Binding var note: String
    let onResolve: () -> Void
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("解决说明（可选）")) {
                    TextEditor(text: $note)
                        .frame(height: 100)
                }
            }
            .navigationTitle("标记已解决")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("取消") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("确认") {
                        onResolve()
                        dismiss()
                    }
                    .fontWeight(.semibold)
                }
            }
        }
        .presentationDetents([.medium])
    }
}

struct MistakeFilterSheet: View {
    @Binding var selectedSubject: String
    @Binding var selectedType: MistakeType
    let subjects: [String]
    @Environment(\.dismiss) var dismiss
    
    var body: some View {
        NavigationView {
            Form {
                Section(header: Text("学科")) {
                    Picker("学科", selection: $selectedSubject) {
                        Text("全部").tag("全部")
                        ForEach(subjects, id: \.self) { subject in
                            Text(subject).tag(subject)
                        }
                    }
                }
                
                Section(header: Text("状态")) {
                    Picker("状态", selection: $selectedType) {
                        Text("全部").tag(MistakeType.all)
                        Text("未解决").tag(MistakeType.unresolved)
                        Text("已解决").tag(MistakeType.resolved)
                        Text("重要").tag(MistakeType.important)
                    }
                }
            }
            .navigationTitle("筛选")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("完成") {
                        dismiss()
                    }
                }
            }
        }
        .presentationDetents([.medium])
    }
}

struct FlowLayout: Layout {
    var spacing: CGFloat = 8
    
    func sizeThatFits(proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) -> CGSize {
        let result = FlowResult(in: proposal.width ?? 0, subviews: subviews, spacing: spacing)
        return result.size
    }
    
    func placeSubviews(in bounds: CGRect, proposal: ProposedViewSize, subviews: Subviews, cache: inout ()) {
        let result = FlowResult(in: bounds.width, subviews: subviews, spacing: spacing)
        for (index, subview) in subviews.enumerated() {
            subview.place(at: CGPoint(x: bounds.minX + result.positions[index].x,
                                      y: bounds.minY + result.positions[index].y),
                         proposal: .unspecified)
        }
    }
    
    struct FlowResult {
        var size: CGSize = .zero
        var positions: [CGPoint] = []
        
        init(in maxWidth: CGFloat, subviews: Subviews, spacing: CGFloat) {
            var x: CGFloat = 0
            var y: CGFloat = 0
            var lineHeight: CGFloat = 0
            
            for subview in subviews {
                let size = subview.sizeThatFits(.unspecified)
                
                if x + size.width > maxWidth, x > 0 {
                    x = 0
                    y += lineHeight + spacing
                    lineHeight = 0
                }
                
                positions.append(CGPoint(x: x, y: y))
                x += size.width + spacing
                lineHeight = max(lineHeight, size.height)
            }
            
            self.size = CGSize(width: maxWidth, height: y + lineHeight)
        }
    }
}

enum MistakeType {
    case all, unresolved, resolved, important
}

@MainActor
class MistakeViewModel: ObservableObject {
    @Published var mistakes: [MistakeModel] = []
    @Published var stats: MistakeStatsModel = MistakeStatsModel(total: 0, unresolved: 0, resolved: 0, important: 0)
    @Published var isLoading = false
    @Published var errorMessage: String?
    
    var subjects: [String] {
        Array(Set(mistakes.map { $0.subject })).sorted()
    }
    
    func loadMistakes() async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            mistakes = try await APIClient.shared.getMistakes()
            stats = MistakeStatsModel(
                total: mistakes.count,
                unresolved: mistakes.filter { !$0.isResolved }.count,
                resolved: mistakes.filter { $0.isResolved }.count,
                important: mistakes.filter { $0.isImportant }.count
            )
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

@MainActor
class MistakeDetailViewModel: ObservableObject {
    @Published var analysis: MistakeAnalysisModel?
    @Published var similarMistakes: [MistakeModel]?
    @Published var resolveHistory: [ResolveHistoryModel] = []
    @Published var isLoading = false
    
    func loadDetail(mistakeId: String) async {
        isLoading = true
        defer { isLoading = false }
        
        do {
            async let analysisTask = APIClient.shared.getMistakeAnalysis(mistakeId: mistakeId)
            async let similarTask = APIClient.shared.getSimilarMistakes(mistakeId: mistakeId)
            async let historyTask = APIClient.shared.getResolveHistory(mistakeId: mistakeId)
            
            analysis = try await analysisTask
            similarMistakes = try await similarTask
            resolveHistory = try await historyTask
        } catch {
            print("Error loading mistake detail: \(error)")
        }
    }
    
    func toggleImportant() {
    }
    
    func resolveMistake(note: String) {
    }
}
