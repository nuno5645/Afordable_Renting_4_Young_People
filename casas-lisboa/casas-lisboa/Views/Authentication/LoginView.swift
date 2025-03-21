import SwiftUI

struct LoginView: View {
    @EnvironmentObject private var authService: AuthenticationService
    @State private var email = ""
    @State private var password = ""
    @State private var isLoading = false
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var showRegistration = false
    @State private var showPassword = false
    
    @FocusState private var focusedField: Field?
    
    private enum Field {
        case email, password
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                Theme.Colors.background.edgesIgnoringSafeArea(.all)
                
                ScrollView {
                    VStack(spacing: 30) {
                        // Header
                        VStack(spacing: 10) {
                            Image(systemName: "house.fill")
                                .font(.system(size: 60))
                                .foregroundColor(Theme.Colors.primary)
                            
                            Text("Welcome Back")
                                .font(.system(size: 34, weight: .bold))
                                .foregroundColor(Theme.Colors.primary)
                            Text("Find your dream home in Lisbon")
                                .font(.subheadline)
                                .foregroundColor(Theme.Colors.secondary)
                        }
                        .padding(.top, 50)
                        
                        // Form Fields
                        VStack(spacing: 20) {
                            // Email Field
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Email")
                                    .font(.callout)
                                    .foregroundColor(Theme.Colors.secondary)
                                TextField("Enter your email", text: $email)
                                    .textFieldStyle(.plain)
                                    .padding()
                                    .glassBackground()
                                    .textContentType(.emailAddress)
                                    .keyboardType(.emailAddress)
                                    .autocapitalization(.none)
                                    .focused($focusedField, equals: .email)
                                    .submitLabel(.next)
                                    .onSubmit {
                                        focusedField = .password
                                    }
                            }
                            
                            // Password Field
                            VStack(alignment: .leading, spacing: 8) {
                                Text("Password")
                                    .font(.callout)
                                    .foregroundColor(Theme.Colors.secondary)
                                HStack {
                                    if showPassword {
                                        TextField("Enter your password", text: $password)
                                            .textContentType(.password)
                                            .focused($focusedField, equals: .password)
                                            .submitLabel(.done)
                                            .onSubmit {
                                                focusedField = nil
                                                Task {
                                                    await login()
                                                }
                                            }
                                    } else {
                                        SecureField("Enter your password", text: $password)
                                            .textContentType(.password)
                                            .focused($focusedField, equals: .password)
                                            .submitLabel(.done)
                                            .onSubmit {
                                                focusedField = nil
                                                Task {
                                                    await login()
                                                }
                                            }
                                    }
                                    
                                    Button(action: { showPassword.toggle() }) {
                                        Image(systemName: showPassword ? "eye.slash.fill" : "eye.fill")
                                            .foregroundColor(Theme.Colors.secondary)
                                    }
                                }
                                .padding()
                                .glassBackground()
                            }
                        }
                        .padding(.horizontal)
                        
                        // Sign In Button
                        Button(action: login) {
                            HStack {
                                if isLoading {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                } else {
                                    Text("Sign In")
                                        .font(.headline)
                                        .fontWeight(.semibold)
                                }
                            }
                            .frame(maxWidth: .infinity)
                            .padding(.vertical, 16)
                            .background(
                                RoundedRectangle(cornerRadius: 15)
                                    .fill(Theme.Colors.primary)
                                    .overlay(
                                        RoundedRectangle(cornerRadius: 15)
                                            .stroke(Color.white.opacity(0.2), lineWidth: 1)
                                    )
                                    .shadow(color: Theme.Colors.primary.opacity(0.5), radius: 10, x: 0, y: 5)
                            )
                            .foregroundColor(.white)
                        }
                        .padding(.horizontal)
                        .disabled(isLoading || email.isEmpty || password.isEmpty)
                        .opacity(email.isEmpty || password.isEmpty ? 0.7 : 1.0)
                        .animation(.easeInOut(duration: 0.2), value: email.isEmpty || password.isEmpty)
                        
                        // Sign Up Link
                        Button {
                            showRegistration = true
                        } label: {
                            Text("Don't have an account? ")
                                .foregroundColor(Theme.Colors.secondary) +
                            Text("Sign Up")
                                .foregroundColor(Theme.Colors.primary)
                                .fontWeight(.semibold)
                        }
                    }
                    .padding(.bottom, 30)
                }
            }
            .alert("Error", isPresented: $showError) {
                Button("OK") { }
            } message: {
                Text(errorMessage)
            }
            .sheet(isPresented: $showRegistration) {
                RegisterView()
            }
            .navigationBarHidden(true)
            .preferredColorScheme(.dark)
        }
    }
    
    private func login() {
        isLoading = true
        Task {
            do {
                try await authService.login(email: email, password: password)
            } catch AuthError.invalidCredentials {
                errorMessage = "Invalid email or password"
                showError = true
            } catch {
                errorMessage = "An error occurred. Please try again."
                showError = true
            }
            isLoading = false
        }
    }
} 