import SwiftUI

struct LoginView: View {
    @StateObject private var viewModel = LoginViewModel()
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        VStack(spacing: 32) {
            Spacer()
            
            VStack(spacing: 8) {
                Image(systemName: "book.circle.fill")
                    .font(.system(size: 80))
                    .foregroundColor(.primaryColor)
                
                Text("智学学生端")
                    .font(.largeTitle)
                    .fontWeight(.bold)
            }
            
            VStack(spacing: 16) {
                TextField("用户名", text: $viewModel.username)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .textContentType(.username)
                    .autocapitalization(.none)
                
                SecureField("密码", text: $viewModel.password)
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .textContentType(.password)
            }
            .padding(.horizontal, 32)
            
            Button(action: {
                viewModel.login { success in
                    if success {
                        appState.isLoggedIn = true
                    }
                }
            }) {
                Text("登录")
                    .font(.headline)
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding()
                    .background(Color.primaryColor)
                    .cornerRadius(10)
            }
            .padding(.horizontal, 32)
            .disabled(viewModel.isLoading)
            
            if viewModel.isLoading {
                ProgressView()
            }
            
            if let error = viewModel.error {
                Text(error)
                    .font(.caption)
                    .foregroundColor(.error)
            }
            
            Spacer()
            
            Text("© 2024 智学教育")
                .font(.caption)
                .foregroundColor(.textHint)
        }
        .background(Color.backgroundColor)
    }
}

class LoginViewModel: ObservableObject {
    @Published var username: String = ""
    @Published var password: String = ""
    @Published var isLoading: Bool = false
    @Published var error: String?
    
    func login(completion: @escaping (Bool) -> Void) {
        guard !username.isEmpty else {
            error = "请输入用户名"
            completion(false)
            return
        }
        
        guard !password.isEmpty else {
            error = "请输入密码"
            completion(false)
            return
        }
        
        isLoading = true
        error = nil
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 1) {
            self.isLoading = false
            
            if self.username == "demo" && self.password == "demo" {
                let user = User(
                    id: "1",
                    name: "张三",
                    email: "demo@example.com",
                    avatar: nil,
                    studentId: "2024001",
                    className: "高三(1)班"
                )
                UserDefaultsManager.shared.saveUser(user)
                KeychainManager.shared.saveToken("demo_token")
                completion(true)
            } else {
                self.error = "用户名或密码错误"
                completion(false)
            }
        }
    }
}

struct LoginView_Previews: PreviewProvider {
    static var previews: some View {
        LoginView()
            .environmentObject(AppState())
    }
}
