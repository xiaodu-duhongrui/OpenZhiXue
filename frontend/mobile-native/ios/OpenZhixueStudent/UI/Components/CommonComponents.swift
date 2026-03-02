import SwiftUI

struct CardView<Content: View>: View {
    let content: Content
    var backgroundColor: Color = .surfaceColor
    var cornerRadius: CGFloat = 12
    var shadowRadius: CGFloat = 2
    var padding: CGFloat = 16
    
    init(backgroundColor: Color = .surfaceColor,
         cornerRadius: CGFloat = 12,
         shadowRadius: CGFloat = 2,
         padding: CGFloat = 16,
         @ViewBuilder content: () -> Content) {
        self.backgroundColor = backgroundColor
        self.cornerRadius = cornerRadius
        self.shadowRadius = shadowRadius
        self.padding = padding
        self.content = content()
    }
    
    var body: some View {
        content
            .padding(padding)
            .background(backgroundColor)
            .cornerRadius(cornerRadius)
            .shadow(color: Color.black.opacity(0.1), radius: shadowRadius, x: 0, y: 1)
    }
}

struct ListItemView: View {
    let title: String
    let subtitle: String?
    let leading: AnyView?
    let trailing: AnyView?
    let action: (() -> Void)?
    
    init(title: String,
         subtitle: String? = nil,
         leading: AnyView? = nil,
         trailing: AnyView? = nil,
         action: (() -> Void)? = nil) {
        self.title = title
        self.subtitle = subtitle
        self.leading = leading
        self.trailing = trailing
        self.action = action
    }
    
    var body: some View {
        Button(action: {
            action?()
        }) {
            HStack(spacing: 12) {
                if let leading = leading {
                    leading
                }
                
                VStack(alignment: .leading, spacing: 4) {
                    Text(title)
                        .font(.headline)
                        .foregroundColor(.textPrimary)
                    
                    if let subtitle = subtitle {
                        Text(subtitle)
                            .font(.subheadline)
                            .foregroundColor(.textSecondary)
                    }
                }
                
                Spacer()
                
                if let trailing = trailing {
                    trailing
                }
            }
            .padding(16)
            .background(Color.surfaceColor)
            .cornerRadius(12)
        }
    }
}

struct LoadingView: View {
    var message: String = "加载中..."
    
    var body: some View {
        VStack(spacing: 16) {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle())
                .scaleEffect(1.2)
            
            Text(message)
                .font(.subheadline)
                .foregroundColor(.textSecondary)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
}

struct EmptyStateView: View {
    let icon: String
    let message: String
    var action: (() -> Void)?
    var actionTitle: String?
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: icon)
                .font(.system(size: 64))
                .foregroundColor(.textHint)
            
            Text(message)
                .font(.headline)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
            
            if let action = action, let actionTitle = actionTitle {
                Button(action: action) {
                    Text(actionTitle)
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding(.horizontal, 24)
                        .padding(.vertical, 12)
                        .background(Color.primaryColor)
                        .cornerRadius(8)
                }
                .padding(.top, 8)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(32)
    }
}

struct ErrorStateView: View {
    let message: String
    let retryAction: (() -> Void)?
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 64))
                .foregroundColor(.error)
            
            Text(message)
                .font(.headline)
                .foregroundColor(.textSecondary)
                .multilineTextAlignment(.center)
            
            if let retryAction = retryAction {
                Button(action: retryAction) {
                    Text("重试")
                        .font(.headline)
                        .foregroundColor(.white)
                        .padding(.horizontal, 24)
                        .padding(.vertical, 12)
                        .background(Color.primaryColor)
                        .cornerRadius(8)
                }
                .padding(.top, 8)
            }
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding(32)
    }
}

struct StatusBadge: View {
    let text: String
    let color: Color
    
    var body: some View {
        Text(text)
            .font(.caption)
            .fontWeight(.medium)
            .foregroundColor(color)
            .padding(.horizontal, 8)
            .padding(.vertical, 4)
            .background(color.opacity(0.1))
            .cornerRadius(8)
    }
}
