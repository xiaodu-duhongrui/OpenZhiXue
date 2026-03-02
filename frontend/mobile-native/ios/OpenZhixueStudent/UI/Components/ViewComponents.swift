import SwiftUI

struct EmptyStateView: View {
    let icon: String
    let title: String
    let subtitle: String?
    let action: (() -> Void)?
    
    init(icon: String, title: String, subtitle: String? = nil, action: (() -> Void)? = nil) {
        self.icon = icon
        self.title = title
        self.subtitle = subtitle
        self.action = action
    }
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 60))
                .foregroundColor(.secondary)
            
            Text(title)
                .font(.headline)
                .foregroundColor(.primary)
            
            if let subtitle = subtitle {
                Text(subtitle)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
            
            if let action = action {
                Button(action: action) {
                    Text("重试")
                        .font(.subheadline)
                        .foregroundColor(.white)
                        .padding(.horizontal, 24)
                        .padding(.vertical, 10)
                        .background(Color(hex: "1890FF"))
                        .cornerRadius(20)
                }
                .padding(.top, 8)
            }
        }
        .padding()
    }
}

struct LoadingView: View {
    let message: String
    
    init(message: String = "加载中...") {
        self.message = message
    }
    
    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
                .scaleEffect(1.2)
            
            Text(message)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
        .padding()
    }
}

struct ErrorView: View {
    let message: String
    let retryAction: (() -> Void)?
    
    init(message: String, retryAction: (() -> Void)? = nil) {
        self.message = message
        self.retryAction = retryAction
    }
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 50))
                .foregroundColor(.orange)
            
            Text(message)
                .font(.subheadline)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
            
            if let retryAction = retryAction {
                Button(action: retryAction) {
                    Text("重试")
                        .font(.subheadline)
                        .foregroundColor(.white)
                        .padding(.horizontal, 24)
                        .padding(.vertical, 10)
                        .background(Color(hex: "1890FF"))
                        .cornerRadius(20)
                }
            }
        }
        .padding()
    }
}

struct AsyncImageView: View {
    let url: URL?
    let placeholder: AnyView
    
    init(url: URL?, @ViewBuilder placeholder: () -> some View) {
        self.url = url
        self.placeholder = AnyView(placeholder())
    }
    
    var body: some View {
        AsyncImage(url: url) { phase in
            switch phase {
            case .empty:
                placeholder
            case .success(let image):
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            case .failure:
                placeholder
            @unknown default:
                placeholder
            }
        }
    }
}

struct BadgeView: View {
    let count: Int
    let color: Color
    
    init(count: Int, color: Color = .red) {
        self.count = count
        self.color = color
    }
    
    var body: some View {
        if count > 0 {
            Text(count > 99 ? "99+" : "\(count)")
                .font(.system(size: 10, weight: .bold))
                .foregroundColor(.white)
                .padding(.horizontal, 6)
                .padding(.vertical, 2)
                .background(color)
                .cornerRadius(10)
                .frame(minWidth: 18)
        }
    }
}

struct ShimmerView: View {
    @State private var phase: CGFloat = 0
    
    var body: some View {
        Rectangle()
            .fill(
                LinearGradient(
                    gradient: Gradient(colors: [
                        Color(hex: "E8E8E8"),
                        Color(hex: "F5F5F5"),
                        Color(hex: "E8E8E8")
                    ]),
                    startPoint: .leading,
                    endPoint: .trailing
                )
            )
            .mask(
                Rectangle()
                    .offset(x: phase)
            )
            .onAppear {
                withAnimation(.linear(duration: 1.5).repeatForever(autoreverses: false)) {
                    phase = 200
                }
            }
    }
}

struct CardView<Content: View>: View {
    let content: Content
    
    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }
    
    var body: some View {
        content
            .padding()
            .background(Color.white)
            .cornerRadius(12)
            .shadow(color: Color.black.opacity(0.05), radius: 5, x: 0, y: 2)
    }
}

struct SectionHeaderView: View {
    let title: String
    let action: (() -> Void)?
    let actionText: String?
    
    init(title: String, actionText: String? = nil, action: (() -> Void)? = nil) {
        self.title = title
        self.action = action
        self.actionText = actionText
    }
    
    var body: some View {
        HStack {
            Text(title)
                .font(.headline)
            
            Spacer()
            
            if let action = action, let actionText = actionText {
                Button(action: action) {
                    HStack(spacing: 4) {
                        Text(actionText)
                            .font(.subheadline)
                        Image(systemName: "chevron.right")
                            .font(.caption)
                    }
                    .foregroundColor(.secondary)
                }
            }
        }
    }
}
