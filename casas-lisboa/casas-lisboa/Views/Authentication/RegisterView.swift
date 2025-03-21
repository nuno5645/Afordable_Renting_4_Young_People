import SwiftUI

struct RegisterView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var authService: AuthenticationService
    
    @State private var email = ""
    @State private var username = ""
    @State private var password = ""
    @State private var confirmPassword = ""
    @State private var showPassword = false
    @State private var showConfirmPassword = false
    @State private var isLoading = false
    @State private var showError = false
    @State private var errorMessage = ""
    
    // Profile fields
    @State private var phoneNumber = ""
    @State private var preferredZones: [String] = []
    @State private var priceRangeMin: Double?
    @State private var priceRangeMax: Double?
    @State private var minBedrooms: Int = 0
    @State private var minArea: Int?
    @State private var notificationEnabled = true
    
    @FocusState private var focusedField: Field?
    
    private enum Field {
        case email, username, password, confirmPassword, phoneNumber, priceRangeMin, priceRangeMax, minBedrooms, minArea
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                Theme.Colors.background.edgesIgnoringSafeArea(.all)
                
                ScrollView {
                    VStack(spacing: 25) {
                        // Account Information Section
                        VStack(alignment: .leading, spacing: 20) {
                            Text("Account Information")
                                .font(.headline)
                                .foregroundColor(Theme.Colors.secondary)
                            
                            VStack(spacing: 15) {
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
                                            focusedField = .username
                                        }
                                }
                                
                                // Username Field
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Username")
                                        .font(.callout)
                                        .foregroundColor(Theme.Colors.secondary)
                                    TextField("Choose a username", text: $username)
                                        .textFieldStyle(.plain)
                                        .padding()
                                        .glassBackground()
                                        .textContentType(.username)
                                        .autocapitalization(.none)
                                        .focused($focusedField, equals: .username)
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
                                            TextField("Create a password", text: $password)
                                                .textContentType(.newPassword)
                                                .focused($focusedField, equals: .password)
                                                .submitLabel(.next)
                                                .onSubmit {
                                                    focusedField = .confirmPassword
                                                }
                                        } else {
                                            SecureField("Create a password", text: $password)
                                                .textContentType(.newPassword)
                                                .focused($focusedField, equals: .password)
                                                .submitLabel(.next)
                                                .onSubmit {
                                                    focusedField = .confirmPassword
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
                                
                                // Confirm Password Field
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Confirm Password")
                                        .font(.callout)
                                        .foregroundColor(Theme.Colors.secondary)
                                    HStack {
                                        if showConfirmPassword {
                                            TextField("Confirm your password", text: $confirmPassword)
                                                .textContentType(.newPassword)
                                                .focused($focusedField, equals: .confirmPassword)
                                                .submitLabel(.next)
                                                .onSubmit {
                                                    focusedField = .phoneNumber
                                                }
                                        } else {
                                            SecureField("Confirm your password", text: $confirmPassword)
                                                .textContentType(.newPassword)
                                                .focused($focusedField, equals: .confirmPassword)
                                                .submitLabel(.next)
                                                .onSubmit {
                                                    focusedField = .phoneNumber
                                                }
                                        }
                                        
                                        Button(action: { showConfirmPassword.toggle() }) {
                                            Image(systemName: showConfirmPassword ? "eye.slash.fill" : "eye.fill")
                                                .foregroundColor(Theme.Colors.secondary)
                                        }
                                    }
                                    .padding()
                                    .glassBackground()
                                }
                            }
                        }
                        .padding(.horizontal)
                        
                        // Profile Information Section
                        VStack(alignment: .leading, spacing: 20) {
                            Text("Profile Information")
                                .font(.headline)
                                .foregroundColor(Theme.Colors.secondary)
                            
                            VStack(spacing: 15) {
                                // Phone Number
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Phone Number")
                                        .font(.callout)
                                        .foregroundColor(Theme.Colors.secondary)
                                    TextField("Enter your phone number", text: $phoneNumber)
                                        .textFieldStyle(.plain)
                                        .padding()
                                        .glassBackground()
                                        .keyboardType(.phonePad)
                                        .focused($focusedField, equals: .phoneNumber)
                                }
                                
                                // Price Range
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Price Range")
                                        .font(.callout)
                                        .foregroundColor(Theme.Colors.secondary)
                                    HStack {
                                        TextField("Min", value: $priceRangeMin, format: .number)
                                            .textFieldStyle(.plain)
                                            .padding()
                                            .glassBackground()
                                            .keyboardType(.numberPad)
                                            .focused($focusedField, equals: .priceRangeMin)
                                        
                                        Text("-")
                                            .foregroundColor(Theme.Colors.secondary)
                                        
                                        TextField("Max", value: $priceRangeMax, format: .number)
                                            .textFieldStyle(.plain)
                                            .padding()
                                            .glassBackground()
                                            .keyboardType(.numberPad)
                                            .focused($focusedField, equals: .priceRangeMax)
                                    }
                                }
                                
                                // Bedrooms
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Minimum Bedrooms")
                                        .font(.callout)
                                        .foregroundColor(Theme.Colors.secondary)
                                    HStack {
                                        Text("\(minBedrooms)")
                                            .frame(width: 30)
                                            .foregroundColor(Theme.Colors.primary)
                                        Stepper("", value: $minBedrooms, in: 0...10)
                                    }
                                    .padding()
                                    .glassBackground()
                                    .focused($focusedField, equals: .minBedrooms)
                                }
                                
                                // Area
                                VStack(alignment: .leading, spacing: 8) {
                                    Text("Minimum Area (m²)")
                                        .font(.callout)
                                        .foregroundColor(Theme.Colors.secondary)
                                    TextField("Enter minimum area", value: $minArea, format: .number)
                                        .textFieldStyle(.plain)
                                        .padding()
                                        .glassBackground()
                                        .keyboardType(.numberPad)
                                        .focused($focusedField, equals: .minArea)
                                }
                                
                                // Notifications
                                Toggle("Enable Notifications", isOn: $notificationEnabled)
                                    .padding()
                                    .glassBackground()
                                    .tint(Theme.Colors.primary)
                            }
                        }
                        .padding(.horizontal)
                        
                        // Create Account Button
                        Button(action: register) {
                            HStack {
                                if isLoading {
                                    ProgressView()
                                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                                } else {
                                    Text("Create Account")
                                        .fontWeight(.semibold)
                                }
                            }
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(isValidForm ? Theme.Colors.primary : Theme.Colors.secondary.opacity(0.5))
                            .foregroundColor(.white)
                            .cornerRadius(10)
                        }
                        .disabled(isLoading || !isValidForm)
                        .padding(.horizontal)
                    }
                    .padding(.vertical, 30)
                }
            }
            .navigationTitle("Create Account")
            .navigationBarTitleDisplayMode(.inline)
            .navigationBarItems(leading: Button("Cancel") {
                dismiss()
            })
            .alert("Error", isPresented: $showError) {
                Button("OK") { }
            } message: {
                Text(errorMessage)
            }
            .preferredColorScheme(.dark)
        }
    }
    
    private var isValidForm: Bool {
        !email.isEmpty &&
        !username.isEmpty &&
        !password.isEmpty &&
        password == confirmPassword &&
        password.count >= 8
    }
    
    private func register() {
        isLoading = true
        
        let profile = UserProfile(
            phoneNumber: phoneNumber.isEmpty ? nil : phoneNumber,
            preferredZones: preferredZones,
            priceRangeMin: priceRangeMin,
            priceRangeMax: priceRangeMax,
            minBedrooms: minBedrooms,
            minArea: minArea,
            notificationEnabled: notificationEnabled
        )
        
        let credentials = RegisterCredentials(
            email: email,
            username: username,
            password: password,
            password2: confirmPassword,
            profile: profile
        )
        
        Task {
            do {
                try await authService.register(credentials: credentials)
                dismiss()
            } catch {
                errorMessage = "Registration failed. Please try again."
                showError = true
            }
            isLoading = false
        }
    }
} 