import SwiftUI

struct ProfileView: View {
    @EnvironmentObject private var authService: AuthenticationService
    @State private var showingLogoutAlert = false
    @State private var isLoading = false
    @State private var showError = false
    @State private var errorMessage = ""
    
    var body: some View {
        NavigationStack {
            ZStack {
                Theme.Colors.background.edgesIgnoringSafeArea(.all)
                
                ScrollView {
                    VStack(spacing: 24) {
                        // Profile Header
                        VStack(spacing: 16) {
                            Image(systemName: "person.circle.fill")
                                .font(.system(size: 80))
                                .foregroundColor(Theme.Colors.primary)
                            
                            if let user = authService.currentUser {
                                Text(user.username)
                                    .font(.title2)
                                    .fontWeight(.semibold)
                                
                                Text(user.email)
                                    .font(.subheadline)
                                    .foregroundColor(Theme.Colors.secondary)
                                
                                if let profile = user.profile {
                                    if let phone = profile.phoneNumber {
                                        Text(phone)
                                            .font(.subheadline)
                                            .foregroundColor(Theme.Colors.secondary)
                                    }
                                }
                            } else {
                                ProgressView()
                                    .tint(Theme.Colors.primary)
                            }
                        }
                        .padding(.vertical, 32)
                        
                        // Settings Sections
                        VStack(spacing: 24) {
                            // Account Settings
                            SettingsSection(title: "Account") {
                                NavigationLink(destination: EditProfileView().environmentObject(authService)) {
                                    SettingsRow(icon: "person.fill", title: "Edit Profile")
                                }
                                
                                NavigationLink(destination: NotificationsView().environmentObject(authService)) {
                                    SettingsRow(icon: "bell.fill", title: "Notifications")
                                }
                                
                                NavigationLink(destination: ChangePasswordView().environmentObject(authService)) {
                                    SettingsRow(icon: "lock.fill", title: "Change Password")
                                }
                                
                                NavigationLink(destination: Text("Privacy Settings").navigationTitle("Privacy")) {
                                    SettingsRow(icon: "hand.raised.fill", title: "Privacy")
                                }
                            }
                            
                            // Support
                            SettingsSection(title: "Support") {
                                NavigationLink(destination: Text("Help Center").navigationTitle("Help Center")) {
                                    SettingsRow(icon: "questionmark.circle.fill", title: "Help Center")
                                }
                                
                                NavigationLink(destination: Text("Contact Us").navigationTitle("Contact Us")) {
                                    SettingsRow(icon: "envelope.fill", title: "Contact Us")
                                }
                                
                                NavigationLink(destination: Text("Terms of Service").navigationTitle("Terms of Service")) {
                                    SettingsRow(icon: "doc.fill", title: "Terms of Service")
                                }
                            }
                        }
                        .padding(.horizontal)
                        
                        // Logout Button
                        Button(action: { showingLogoutAlert = true }) {
                            HStack {
                                Image(systemName: "rectangle.portrait.and.arrow.right")
                                Text("Logout")
                            }
                            .foregroundColor(.red)
                            .padding()
                            .frame(maxWidth: .infinity)
                            .glassBackground()
                        }
                        .padding(.horizontal)
                    }
                }
            }
            .navigationTitle("Profile")
            .alert("Logout", isPresented: $showingLogoutAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Logout", role: .destructive) {
                    Task {
                        isLoading = true
                        do {
                            try await authService.logout()
                        } catch {
                            print("❌ Logout failed: \(error)")
                        }
                        isLoading = false
                    }
                }
            } message: {
                Text("Are you sure you want to logout?")
            }
            .alert("Error", isPresented: $showError) {
                Button("OK", role: .cancel) { }
            } message: {
                Text(errorMessage)
            }
            .overlay {
                if isLoading {
                    Color.black.opacity(0.3)
                        .edgesIgnoringSafeArea(.all)
                        .overlay {
                            ProgressView()
                                .tint(.white)
                        }
                }
            }
        }
    }
}

struct EditProfileView: View {
    @EnvironmentObject var authService: AuthenticationService
    @State private var minPrice: Double?
    @State private var maxPrice: Double?
    @State private var minBedrooms: Int?
    @State private var minArea: Int?
    @State private var isLoading = false
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var showSuccess = false
    
    @FocusState private var focusedField: Field?
    
    private enum Field {
        case minPrice, maxPrice, minBedrooms, minArea
    }
    
    var body: some View {
        Form {
            Section(header: Text("Personal Information")) {
                if let user = authService.currentUser {
                    HStack {
                        Text("Username")
                        Spacer()
                        Text(user.username)
                            .foregroundColor(Theme.Colors.secondary)
                    }
                    
                    HStack {
                        Text("Email")
                        Spacer()
                        Text(user.email)
                            .foregroundColor(Theme.Colors.secondary)
                    }
                }
            }
            
            Section(header: Text("Search Preferences - Price Range")) {
                HStack {
                    Text("Min Price")
                    Spacer()
                    TextField("€", value: $minPrice, format: .number)
                        .keyboardType(.numberPad)
                        .multilineTextAlignment(.trailing)
                        .focused($focusedField, equals: .minPrice)
                        .submitLabel(.next)
                        .onSubmit {
                            focusedField = .maxPrice
                        }
                }
                
                HStack {
                    Text("Max Price")
                    Spacer()
                    TextField("€", value: $maxPrice, format: .number)
                        .keyboardType(.numberPad)
                        .multilineTextAlignment(.trailing)
                        .focused($focusedField, equals: .maxPrice)
                        .submitLabel(.next)
                        .onSubmit {
                            focusedField = .minBedrooms
                        }
                }
            }
            
            Section(header: Text("Search Preferences - Property Details")) {
                HStack {
                    Text("Min Bedrooms")
                    Spacer()
                    TextField("0", value: $minBedrooms, format: .number)
                        .keyboardType(.numberPad)
                        .multilineTextAlignment(.trailing)
                        .focused($focusedField, equals: .minBedrooms)
                        .submitLabel(.next)
                        .onSubmit {
                            focusedField = .minArea
                        }
                }
                
                HStack {
                    Text("Min Area (m²)")
                    Spacer()
                    TextField("0", value: $minArea, format: .number)
                        .keyboardType(.numberPad)
                        .multilineTextAlignment(.trailing)
                        .focused($focusedField, equals: .minArea)
                        .submitLabel(.done)
                        .onSubmit {
                            focusedField = nil
                            savePreferences()
                        }
                }
            }
            
            Section {
                Button("Save Changes") {
                    savePreferences()
                }
                .frame(maxWidth: .infinity, alignment: .center)
                .foregroundColor(Theme.Colors.primary)
            }
        }
        .navigationTitle("Edit Profile")
        .onAppear {
            loadCurrentPreferences()
        }
        .alert("Error", isPresented: $showError) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(errorMessage)
        }
        .overlay {
            if isLoading {
                Color.black.opacity(0.3)
                    .edgesIgnoringSafeArea(.all)
                    .overlay {
                        ProgressView()
                            .tint(.white)
                    }
            }
            
            if showSuccess {
                VStack {
                    Spacer()
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text("Preferences saved successfully")
                            .foregroundColor(.white)
                    }
                    .padding()
                    .background(Color.black.opacity(0.7))
                    .cornerRadius(10)
                    .padding(.bottom, 20)
                }
                .transition(.move(edge: .bottom))
                .animation(.easeInOut, value: showSuccess)
            }
        }
    }
    
    private func loadCurrentPreferences() {
        if let profile = authService.currentUser?.profile {
            minPrice = profile.priceRangeMin
            maxPrice = profile.priceRangeMax
            minBedrooms = profile.minBedrooms
            minArea = profile.minArea
        }
    }
    
    private func savePreferences() {
        isLoading = true
        Task {
            do {
                let notificationEnabled = authService.currentUser?.profile?.notificationEnabled ?? true
                
                let updatedUser = try await NetworkService.shared.updateUserPreferences(
                    minPrice: minPrice,
                    maxPrice: maxPrice,
                    minBedrooms: minBedrooms,
                    minArea: minArea,
                    notificationEnabled: notificationEnabled
                )
                await MainActor.run {
                    authService.currentUser = updatedUser
                    isLoading = false
                    showSuccess = true
                    // Hide success message after 2 seconds
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        showSuccess = false
                    }
                }
            } catch {
                await MainActor.run {
                    errorMessage = "Failed to update preferences. Please try again."
                    showError = true
                    isLoading = false
                }
            }
        }
    }
}

struct NotificationsView: View {
    @EnvironmentObject var authService: AuthenticationService
    @State private var notificationEnabled: Bool = true
    @State private var isLoading = false
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var showSuccess = false
    
    var body: some View {
        Form {
            Section {
                Toggle("Enable Notifications", isOn: $notificationEnabled)
                    .onChange(of: notificationEnabled) { newValue in
                        saveNotificationPreference(newValue)
                    }
                
                Text("You will receive notifications when new properties matching your preferences are found.")
                    .font(.caption)
                    .foregroundColor(Theme.Colors.secondary)
            }
        }
        .navigationTitle("Notifications")
        .onAppear {
            loadCurrentPreferences()
        }
        .alert("Error", isPresented: $showError) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(errorMessage)
        }
        .overlay {
            if isLoading {
                Color.black.opacity(0.3)
                    .edgesIgnoringSafeArea(.all)
                    .overlay {
                        ProgressView()
                            .tint(.white)
                    }
            }
            
            if showSuccess {
                VStack {
                    Spacer()
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text("Notification settings saved successfully")
                            .foregroundColor(.white)
                    }
                    .padding()
                    .background(Color.black.opacity(0.7))
                    .cornerRadius(10)
                    .padding(.bottom, 20)
                }
                .transition(.move(edge: .bottom))
                .animation(.easeInOut, value: showSuccess)
            }
        }
    }
    
    private func loadCurrentPreferences() {
        if let profile = authService.currentUser?.profile {
            notificationEnabled = profile.notificationEnabled
        }
    }
    
    private func saveNotificationPreference(_ enabled: Bool) {
        isLoading = true
        Task {
            do {
                // Get current preferences values
                let profile = authService.currentUser?.profile
                
                let updatedUser = try await NetworkService.shared.updateUserPreferences(
                    minPrice: profile?.priceRangeMin,
                    maxPrice: profile?.priceRangeMax,
                    minBedrooms: profile?.minBedrooms,
                    minArea: profile?.minArea,
                    notificationEnabled: enabled
                )
                await MainActor.run {
                    authService.currentUser = updatedUser
                    isLoading = false
                    showSuccess = true
                    // Hide success message after 2 seconds
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        withAnimation {
                            showSuccess = false
                        }
                    }
                }
            } catch {
                await MainActor.run {
                    errorMessage = "Failed to update notification settings. Please try again."
                    showError = true
                    isLoading = false
                }
            }
        }
    }
}

struct SettingsSection<Content: View>: View {
    let title: String
    let content: Content
    
    init(title: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(title)
                .font(.headline)
                .foregroundColor(Theme.Colors.secondary)
                .padding(.leading, 4)
            
            VStack(spacing: 0) {
                content
            }
            .glassBackground()
        }
    }
}

struct SettingsRow: View {
    let icon: String
    let title: String
    
    var body: some View {
        HStack(spacing: 12) {
            Image(systemName: icon)
                .font(.system(size: 18))
                .foregroundColor(Theme.Colors.primary)
                .frame(width: 24)
            
            Text(title)
                .foregroundColor(Theme.Colors.primary)
            
            Spacer()
            
            Image(systemName: "chevron.right")
                .font(.system(size: 14))
                .foregroundColor(Theme.Colors.secondary)
        }
        .padding()
    }
}

struct ChangePasswordView: View {
    @Environment(\.dismiss) private var dismiss
    @EnvironmentObject private var authService: AuthenticationService
    
    @State private var oldPassword = ""
    @State private var newPassword = ""
    @State private var confirmPassword = ""
    @State private var showOldPassword = false
    @State private var showNewPassword = false
    @State private var showConfirmPassword = false
    @State private var isLoading = false
    @State private var showError = false
    @State private var errorMessage = ""
    @State private var showSuccess = false
    
    @FocusState private var focusedField: Field?
    
    private enum Field {
        case oldPassword, newPassword, confirmPassword
    }
    
    var body: some View {
        Form {
            Section {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Current Password")
                        .font(.callout)
                        .foregroundColor(Theme.Colors.secondary)
                    HStack {
                        if showOldPassword {
                            TextField("Enter current password", text: $oldPassword)
                                .textContentType(.password)
                                .focused($focusedField, equals: .oldPassword)
                                .submitLabel(.next)
                                .onSubmit {
                                    focusedField = .newPassword
                                }
                        } else {
                            SecureField("Enter current password", text: $oldPassword)
                                .textContentType(.password)
                                .focused($focusedField, equals: .oldPassword)
                                .submitLabel(.next)
                                .onSubmit {
                                    focusedField = .newPassword
                                }
                        }
                        
                        Button(action: { showOldPassword.toggle() }) {
                            Image(systemName: showOldPassword ? "eye.slash.fill" : "eye.fill")
                                .foregroundColor(Theme.Colors.secondary)
                        }
                    }
                    .padding()
                    .glassBackground()
                }
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("New Password")
                        .font(.callout)
                        .foregroundColor(Theme.Colors.secondary)
                    HStack {
                        if showNewPassword {
                            TextField("Enter new password", text: $newPassword)
                                .textContentType(.newPassword)
                                .focused($focusedField, equals: .newPassword)
                                .submitLabel(.next)
                                .onSubmit {
                                    focusedField = .confirmPassword
                                }
                        } else {
                            SecureField("Enter new password", text: $newPassword)
                                .textContentType(.newPassword)
                                .focused($focusedField, equals: .newPassword)
                                .submitLabel(.next)
                                .onSubmit {
                                    focusedField = .confirmPassword
                                }
                        }
                        
                        Button(action: { showNewPassword.toggle() }) {
                            Image(systemName: showNewPassword ? "eye.slash.fill" : "eye.fill")
                                .foregroundColor(Theme.Colors.secondary)
                        }
                    }
                    .padding()
                    .glassBackground()
                }
                
                VStack(alignment: .leading, spacing: 8) {
                    Text("Confirm New Password")
                        .font(.callout)
                        .foregroundColor(Theme.Colors.secondary)
                    HStack {
                        if showConfirmPassword {
                            TextField("Confirm new password", text: $confirmPassword)
                                .textContentType(.newPassword)
                                .focused($focusedField, equals: .confirmPassword)
                                .submitLabel(.done)
                                .onSubmit {
                                    focusedField = nil
                                    changePassword()
                                }
                        } else {
                            SecureField("Confirm new password", text: $confirmPassword)
                                .textContentType(.newPassword)
                                .focused($focusedField, equals: .confirmPassword)
                                .submitLabel(.done)
                                .onSubmit {
                                    focusedField = nil
                                    changePassword()
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
            
            Section {
                Button("Change Password") {
                    changePassword()
                }
                .frame(maxWidth: .infinity, alignment: .center)
                .foregroundColor(Theme.Colors.primary)
                .disabled(isLoading || !isValidForm)
            }
        }
        .navigationTitle("Change Password")
        .alert("Error", isPresented: $showError) {
            Button("OK", role: .cancel) { }
        } message: {
            Text(errorMessage)
        }
        .overlay {
            if isLoading {
                Color.black.opacity(0.3)
                    .edgesIgnoringSafeArea(.all)
                    .overlay {
                        ProgressView()
                            .tint(.white)
                    }
            }
            
            if showSuccess {
                VStack {
                    Spacer()
                    HStack {
                        Image(systemName: "checkmark.circle.fill")
                            .foregroundColor(.green)
                        Text("Password changed successfully")
                            .foregroundColor(.white)
                    }
                    .padding()
                    .background(Color.black.opacity(0.7))
                    .cornerRadius(10)
                    .padding(.bottom, 20)
                }
                .transition(.move(edge: .bottom))
                .animation(.easeInOut, value: showSuccess)
            }
        }
    }
    
    private var isValidForm: Bool {
        !oldPassword.isEmpty &&
        !newPassword.isEmpty &&
        !confirmPassword.isEmpty &&
        newPassword == confirmPassword &&
        newPassword.count >= 8
    }
    
    private func changePassword() {
        guard isValidForm else { return }
        
        isLoading = true
        Task {
            do {
                try await authService.changePassword(oldPassword: oldPassword, newPassword: newPassword)
                await MainActor.run {
                    isLoading = false
                    showSuccess = true
                    oldPassword = ""
                    newPassword = ""
                    confirmPassword = ""
                    // Hide success message after 2 seconds
                    DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
                        showSuccess = false
                    }
                }
            } catch AuthError.invalidCredentials {
                await MainActor.run {
                    errorMessage = "Current password is incorrect"
                    showError = true
                    isLoading = false
                }
            } catch {
                await MainActor.run {
                    errorMessage = "Failed to change password. Please try again."
                    showError = true
                    isLoading = false
                }
            }
        }
    }
}

#Preview {
    ProfileView()
        .environmentObject(AuthenticationService())
        .preferredColorScheme(.dark)
}