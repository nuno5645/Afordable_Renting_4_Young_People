import SwiftUI

struct ProfileView: View {
    @State private var showingLogoutAlert = false
    
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
                            
                            Text("John Doe")
                                .font(.title2)
                                .fontWeight(.semibold)
                            
                            Text("john.doe@example.com")
                                .font(.subheadline)
                                .foregroundColor(Theme.Colors.secondary)
                        }
                        .padding(.vertical, 32)
                        
                        // Settings Sections
                        VStack(spacing: 24) {
                            // Account Settings
                            SettingsSection(title: "Account") {
                                SettingsRow(icon: "person.fill", title: "Edit Profile")
                                SettingsRow(icon: "bell.fill", title: "Notifications")
                                SettingsRow(icon: "lock.fill", title: "Privacy")
                            }
                            
                            // Preferences
                            SettingsSection(title: "Preferences") {
                                SettingsRow(icon: "globe", title: "Language")
                                SettingsRow(icon: "moon.fill", title: "Dark Mode")
                                SettingsRow(icon: "bell.badge.fill", title: "Push Notifications")
                            }
                            
                            // Support
                            SettingsSection(title: "Support") {
                                SettingsRow(icon: "questionmark.circle.fill", title: "Help Center")
                                SettingsRow(icon: "envelope.fill", title: "Contact Us")
                                SettingsRow(icon: "doc.fill", title: "Terms of Service")
                            }
                        }
                        .padding(.horizontal)
                        
                        // Logout Button
                        Button(action: {
                            showingLogoutAlert = true
                        }) {
                            HStack {
                                Image(systemName: "rectangle.portrait.and.arrow.right")
                                Text("Logout")
                            }
                            .foregroundColor(.red)
                            .padding()
                            .frame(maxWidth: .infinity)
                            .glassBackground()
                            .padding(.horizontal)
                        }
                    }
                }
            }
            .navigationTitle("Profile")
            .alert("Logout", isPresented: $showingLogoutAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Logout", role: .destructive) {
                    // Handle logout
                }
            } message: {
                Text("Are you sure you want to logout?")
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
        Button(action: {}) {
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
}

#Preview {
    ProfileView()
        .preferredColorScheme(.dark)
} 