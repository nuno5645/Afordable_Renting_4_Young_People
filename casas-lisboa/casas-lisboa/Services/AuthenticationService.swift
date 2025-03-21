import Foundation
import KeychainSwift

enum AuthError: Error {
    case invalidCredentials
    case networkError(Error)
    case decodingError
    case tokenExpired
    case unknown
    case invalidResponse
    case unauthorized
}

@MainActor
class AuthenticationService: ObservableObject {
    #if targetEnvironment(simulator)
        private let baseURL = "https://localhost:8080/api/users"
    #else
        private let baseURL = "https://100.95.208.157:8080/api/users"
    #endif
    
    private let keychain = KeychainSwift()
    private let session: URLSession
    
    @Published var currentUser: User?
    @Published var isAuthenticated = false
    
    init() {
        print("🔐 AuthService: Initializing with base URL: \(baseURL)")
        // Use NetworkService's session for SSL certificate handling
        self.session = NetworkService.shared.session
        
        // Check for existing tokens and validate them
        if let accessToken = keychain.get("accessToken") {
            print("🔐 AuthService: Found existing access token")
            self.isAuthenticated = true
            Task {
                await getCurrentUser()
            }
        }
    }
    
    func login(email: String, password: String) async throws {
        print("🔐 AuthService: Attempting login for email: \(email)")
        let credentials = LoginCredentials(email: email, password: password)
        
        guard let url = URL(string: "\(baseURL)/login/") else {
            print("❌ AuthService: Invalid URL for login")
            throw AuthError.unknown
        }
        
        print("🔐 AuthService: Making login request to: \(url.absoluteString)")
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(credentials)
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ AuthService: Invalid HTTP response")
                throw AuthError.unknown
            }
            
            print("🔐 AuthService: Received response with status code: \(httpResponse.statusCode)")
            
            if httpResponse.statusCode == 401 {
                print("❌ AuthService: Invalid credentials")
                throw AuthError.invalidCredentials
            }
            
            if let responseString = String(data: data, encoding: .utf8) {
                print("🔐 AuthService: Response data: \(responseString)")
            }
            
            let authResponse = try JSONDecoder().decode(AuthResponse.self, from: data)
            print("🔐 AuthService: Successfully decoded auth response")
            
            // Store tokens
            keychain.set(authResponse.access, forKey: "accessToken")
            keychain.set(authResponse.refresh, forKey: "refreshToken")
            
            isAuthenticated = true
            await getCurrentUser()
            print("🔐 AuthService: Login successful")
            
        } catch {
            print("❌ AuthService: Login error: \(error)")
            throw AuthError.networkError(error)
        }
    }
    
    func register(credentials: RegisterCredentials) async throws {
        print("🔐 AuthService: Attempting registration for email: \(credentials.email)")
        guard let url = URL(string: "\(baseURL)/register/") else {
            print("❌ AuthService: Invalid URL for registration")
            throw AuthError.unknown
        }
        
        print("🔐 AuthService: Making registration request to: \(url.absoluteString)")
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        // Debug the request body
        let jsonData = try JSONEncoder().encode(credentials)
        if let jsonString = String(data: jsonData, encoding: .utf8) {
            print("🔐 AuthService: Request body: \(jsonString)")
        }
        request.httpBody = jsonData
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ AuthService: Invalid HTTP response")
                throw AuthError.unknown
            }
            
            print("🔐 AuthService: Received response with status code: \(httpResponse.statusCode)")
            
            if let responseString = String(data: data, encoding: .utf8) {
                print("🔐 AuthService: Response data: \(responseString)")
            }
            
            if httpResponse.statusCode != 201 {
                print("❌ AuthService: Registration failed with status code: \(httpResponse.statusCode)")
                throw AuthError.invalidCredentials
            }
            
            // After successful registration, login with the same credentials
            print("🔐 AuthService: Registration successful, attempting login")
            try await login(email: credentials.email, password: credentials.password)
            
        } catch {
            print("❌ AuthService: Registration error: \(error)")
            throw AuthError.networkError(error)
        }
    }
    
    func logout() async throws {
        print("🔐 AuthService: Attempting logout")
        guard let refreshToken = keychain.get("refreshToken"),
              let url = URL(string: "\(baseURL)/logout/") else {
            print("❌ AuthService: Invalid URL for logout or no refresh token")
            throw AuthError.unknown
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(keychain.get("accessToken") ?? "")", forHTTPHeaderField: "Authorization")
        
        // Create the correct request body format
        let body = ["refresh_token": refreshToken]
        request.httpBody = try JSONEncoder().encode(body)
        
        do {
            let (_, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ AuthService: Invalid HTTP response")
                throw AuthError.unknown
            }
            
            print("🔐 AuthService: Received logout response with status code: \(httpResponse.statusCode)")
            
            if httpResponse.statusCode == 200 {
                // Clear stored tokens and user data
                keychain.delete("accessToken")
                keychain.delete("refreshToken")
                currentUser = nil
                isAuthenticated = false
                print("🔐 AuthService: Logout successful")
            } else {
                print("❌ AuthService: Logout failed with status code: \(httpResponse.statusCode)")
                throw AuthError.unknown
            }
            
        } catch {
            print("❌ AuthService: Logout error: \(error)")
            throw AuthError.networkError(error)
        }
    }
    
    func getCurrentUser() async {
        print("🔐 AuthService: Fetching current user profile")
        guard let url = URL(string: "\(baseURL)/profile/") else {
            print("❌ AuthService: Invalid URL for profile")
            return
        }
        
        var request = URLRequest(url: url)
        request.setValue("Bearer \(keychain.get("accessToken") ?? "")", forHTTPHeaderField: "Authorization")
        
        do {
            let (data, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🔐 AuthService: Received profile response with status code: \(httpResponse.statusCode)")
            }
            
            if let responseString = String(data: data, encoding: .utf8) {
                print("🔐 AuthService: Profile response data: \(responseString)")
            }
            
            currentUser = try JSONDecoder().decode(User.self, from: data)
            print("🔐 AuthService: Successfully fetched user profile")
        } catch {
            print("❌ AuthService: Error fetching current user: \(error)")
        }
    }
    
    func refreshToken() async throws -> String {
        print("🔐 AuthService: Attempting to refresh token")
        guard let refreshToken = keychain.get("refreshToken"),
              let url = URL(string: "\(baseURL)/login/refresh/") else {
            print("❌ AuthService: Invalid URL for token refresh or no refresh token")
            throw AuthError.unknown
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let refreshRequest = TokenRefreshRequest(refresh: refreshToken)
        request.httpBody = try JSONEncoder().encode(refreshRequest)
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ AuthService: Invalid HTTP response")
                throw AuthError.unknown
            }
            
            print("🔐 AuthService: Received token refresh response with status code: \(httpResponse.statusCode)")
            
            if httpResponse.statusCode == 401 {
                print("❌ AuthService: Token refresh failed - expired token")
                throw AuthError.tokenExpired
            }
            
            let authResponse = try JSONDecoder().decode(AuthResponse.self, from: data)
            keychain.set(authResponse.access, forKey: "accessToken")
            print("🔐 AuthService: Successfully refreshed token")
            
            return authResponse.access
            
        } catch {
            print("❌ AuthService: Token refresh error: \(error)")
            throw AuthError.networkError(error)
        }
    }
    
    func updateProfile(_ profile: UserProfile) async throws {
        print("🔐 AuthService: Attempting to update user profile")
        guard let url = URL(string: "\(baseURL)/profile/") else {
            print("❌ AuthService: Invalid URL for profile update")
            throw AuthError.unknown
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "PATCH"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(keychain.get("accessToken") ?? "")", forHTTPHeaderField: "Authorization")
        
        // Debug the request body
        let jsonData = try JSONEncoder().encode(profile)
        if let jsonString = String(data: jsonData, encoding: .utf8) {
            print("🔐 AuthService: Profile update request body: \(jsonString)")
        }
        request.httpBody = jsonData
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ AuthService: Invalid HTTP response")
                throw AuthError.unknown
            }
            
            print("🔐 AuthService: Received profile update response with status code: \(httpResponse.statusCode)")
            
            if httpResponse.statusCode != 200 {
                print("❌ AuthService: Profile update failed")
                throw AuthError.unknown
            }
            
            let updatedUser = try JSONDecoder().decode(User.self, from: data)
            currentUser = updatedUser
            print("🔐 AuthService: Successfully updated user profile")
            
        } catch {
            print("❌ AuthService: Profile update error: \(error)")
            throw AuthError.networkError(error)
        }
    }
    
    func fetchCurrentUser() async throws -> User {
        print("🔐 AuthService: Fetching current user profile")
        guard let url = URL(string: "\(baseURL)/profile/") else {
            throw AuthError.unknown
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        if let token = keychain.get("accessToken") {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse else {
            throw AuthError.invalidResponse
        }
        
        print("🔐 AuthService: Received profile response with status code: \(httpResponse.statusCode)")
        print("🔐 AuthService: Profile response data: \(String(data: data, encoding: .utf8) ?? "nil")")
        
        if httpResponse.statusCode == 401 {
            throw AuthError.unauthorized
        }
        
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try decoder.decode(User.self, from: data)
    }
    
    func changePassword(oldPassword: String, newPassword: String) async throws {
        print("🔐 AuthService: Attempting to change password")
        guard let url = URL(string: "\(baseURL)/password/change/") else {
            print("❌ AuthService: Invalid URL for password change")
            throw AuthError.unknown
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "PATCH"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue("Bearer \(keychain.get("accessToken") ?? "")", forHTTPHeaderField: "Authorization")
        
        let body = [
            "old_password": oldPassword,
            "new_password": newPassword,
            "new_password2": newPassword  // Adding confirmation password
        ]
        
        request.httpBody = try JSONEncoder().encode(body)
        
        do {
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse else {
                print("❌ AuthService: Invalid HTTP response")
                throw AuthError.unknown
            }
            
            print("🔐 AuthService: Received password change response with status code: \(httpResponse.statusCode)")
            
            if let responseString = String(data: data, encoding: .utf8) {
                print("🔐 AuthService: Response data: \(responseString)")
            }
            
            if httpResponse.statusCode == 400 {
                print("❌ AuthService: Invalid old password")
                throw AuthError.invalidCredentials
            }
            
            if httpResponse.statusCode != 200 {
                print("❌ AuthService: Password change failed")
                throw AuthError.unknown
            }
            
            print("🔐 AuthService: Successfully changed password")
            
        } catch {
            print("❌ AuthService: Password change error: \(error)")
            throw AuthError.networkError(error)
        }
    }
} 