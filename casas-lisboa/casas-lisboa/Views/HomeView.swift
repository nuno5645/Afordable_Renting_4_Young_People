import SwiftUI
import MessageUI

// MARK: - Navigation Bar View
struct CustomNavigationBar: View {
    let title: String
    let onFilterTap: () -> Void
    @State private var isPressed = false
    
    var body: some View {
        HStack {
            Text(title)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(Theme.Colors.primary)
            
            Spacer()
            
            Button(action: {
                isPressed.toggle()
                onFilterTap()
            }) {
                HStack(spacing: 6) {
                    Image(systemName: "line.3.horizontal.decrease")
                        .rotationEffect(.degrees(isPressed ? -10 : 0))
                        .animation(.spring(response: 0.3, dampingFraction: 0.6), value: isPressed)
                    Text("Filters")
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .glassBackground()
            }
            .filterButtonStyle()
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
        .background(Theme.Colors.background)
    }
}

// MARK: - Contact Sheet View
struct ContactOptionsSheet: View {
    let property: Property
    @Environment(\.dismiss) var dismiss
    @State private var showingMailView = false
    @State private var mailResult: Result<MFMailComposeResult, Error>?
    
    var body: some View {
        NavigationView {
            List {
                Section {
                    ContactOptionButton(
                        icon: "phone.fill",
                        text: "Call Agent",
                        iconColor: .green
                    ) {
                        if let url = URL(string: "tel://+351912345678") {
                            UIApplication.shared.open(url)
                            dismiss()
                        }
                    }
                    
                    ContactOptionButton(
                        icon: "envelope.fill",
                        text: "Email Agent",
                        iconColor: .blue
                    ) {
                        showingMailView = true
                    }
                    
                    ContactOptionButton(
                        icon: "message.fill",
                        text: "WhatsApp",
                        iconColor: .green
                    ) {
                        if let url = URL(string: "https://wa.me/351912345678") {
                            UIApplication.shared.open(url)
                            dismiss()
                        }
                    }
                } header: {
                    Text("Contact Options")
                } footer: {
                    Text("Property: \(property.location)")
                }
            }
            .navigationTitle("Contact Agent")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Done") {
                        dismiss()
                    }
                }
            }
        }
        .sheet(isPresented: $showingMailView) {
            MailView(result: $mailResult) { composer in
                composer.setToRecipients(["agent@example.com"])
                composer.setSubject("Inquiry about property in \(property.location)")
                composer.setMessageBody("Hi, I'm interested in the property listed at \(property.location) for \(property.formattedPrice).", isHTML: false)
            }
        }
    }
}

struct ContactOptionButton: View {
    let icon: String
    let text: String
    let iconColor: Color
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            HStack {
                Image(systemName: icon)
                    .foregroundColor(iconColor)
                Text(text)
            }
        }
    }
}

// MARK: - Mail View
struct MailView: UIViewControllerRepresentable {
    @Binding var result: Result<MFMailComposeResult, Error>?
    @Environment(\.dismiss) var dismiss
    let configure: (MFMailComposeViewController) -> Void
    
    func makeUIViewController(context: Context) -> MFMailComposeViewController {
        let composer = MFMailComposeViewController()
        composer.mailComposeDelegate = context.coordinator
        configure(composer)
        return composer
    }
    
    func updateUIViewController(_ uiViewController: MFMailComposeViewController, context: Context) {}
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    class Coordinator: NSObject, MFMailComposeViewControllerDelegate {
        let parent: MailView
        
        init(_ parent: MailView) {
            self.parent = parent
        }
        
        func mailComposeController(_ controller: MFMailComposeViewController, didFinishWith result: MFMailComposeResult, error: Error?) {
            if let error = error {
                parent.result = .failure(error)
            } else {
                parent.result = .success(result)
            }
            parent.dismiss()
        }
    }
}

// MARK: - Property Card Container
struct PropertyCardContainer: View {
    let property: Property
    let onPropertyUpdate: (Property) -> Void
    let onPropertyRemove: (Property) -> Void
    @StateObject private var stateManager = PropertyStateManager.shared
    
    var body: some View {
        PropertyCardView(
            property: property,
            onFavoriteToggle: { updatedProperty in
                print("🏠 Handling favorite toggle for house: \(updatedProperty.houseId)")
                Task {
                    do {
                        try await NetworkService.shared.toggleFavorite(for: updatedProperty.houseId)
                        onPropertyUpdate(updatedProperty)
                    } catch {
                        print("❌ Failed to toggle favorite: \(error.localizedDescription)")
                        // Revert the state if the API call fails
                        stateManager.toggleFavorite(updatedProperty.houseId)
                    }
                }
            },
            onDelete: nil,
            onContactedChange: { property in
                print("🏠 Handling contacted change for house: \(property.houseId)")
                Task {
                    do {
                        try await NetworkService.shared.toggleContacted(for: property.houseId)
                        onPropertyUpdate(property)
                    } catch {
                        print("❌ Failed to toggle contacted: \(error.localizedDescription)")
                        // Revert the state if the API call fails
                        stateManager.toggleContacted(property.houseId)
                    }
                }
            },
            onDiscard: { property in
                print("🏠 Starting discard process for house: \(property.houseId)")
                // Update local state immediately
                stateManager.toggleDiscarded(property.houseId)
                
                // Remove from UI immediately
                onPropertyRemove(property)
                
                // Then update the server
                Task {
                    do {
                        print("🏠 Calling toggleDiscarded API for house: \(property.houseId)")
                        try await NetworkService.shared.toggleDiscarded(for: property.houseId)
                        print("🏠 API call successful")
                    } catch {
                        print("❌ Failed to discard property: \(error.localizedDescription)")
                        print("❌ Error details: \(error)")
                        // Note: We don't revert the UI state here since the item is already removed
                    }
                }
            }
        )
        .transition(.opacity.combined(with: .move(edge: .leading)))
    }
}

// MARK: - Home View
struct HomeView: View {
    @StateObject private var viewModel = HomeViewModel()
    @EnvironmentObject var authService: AuthenticationService
    @State private var showingLoginSheet = false
    @State private var isRefreshingToken = false
    @State private var properties: [Property] = []
    @State private var showFilterSheet = false
    @State private var selectedProperty: Property?
    @State private var searchText = ""
    @State private var showContactSheet = false
    @StateObject private var stateManager = PropertyStateManager.shared
    
    var filteredProperties: [Property] {
        FilterOptions().filterProperties(properties)
    }
    
    var body: some View {
        NavigationView {
            Group {
                if viewModel.isLoading {
                    LoadingView()
                } else if let error = viewModel.error {
                    ErrorView(error: error) {
                        Task {
                            await loadProperties()
                        }
                    }
                } else {
                    propertyList
                }
            }
            .navigationTitle("Houses")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        Task {
                            await loadProperties()
                        }
                    }) {
                        Image(systemName: "arrow.clockwise")
                    }
                }
            }
        }
        .sheet(isPresented: $showingLoginSheet) {
            LoginView()
        }
        .onAppear {
            Task {
                await loadProperties()
            }
        }
        .accentColor(Theme.Colors.primary)
        .preferredColorScheme(.dark)
        .filterSheet(isPresented: $showFilterSheet, filterOptions: FilterOptions())
        .sheet(isPresented: $showContactSheet, content: {
            if let property = selectedProperty {
                ContactOptionsSheet(property: property)
            }
        })
    }
    
    private var propertyList: some View {
        ScrollView {
            LazyVStack(spacing: 16) {
                ForEach(filteredProperties) { property in
                    PropertyCardContainer(
                        property: property,
                        onPropertyUpdate: { updatedProperty in
                            if let index = properties.firstIndex(where: { $0.id == updatedProperty.id }) {
                                withAnimation {
                                    if updatedProperty.isFavorite != properties[index].isFavorite {
                                        properties[index].isFavorite.toggle()
                                    }
                                    if updatedProperty.contacted != properties[index].contacted {
                                        properties[index].contacted.toggle()
                                    }
                                }
                            }
                        },
                        onPropertyRemove: { property in
                            withAnimation {
                                properties.removeAll { $0.id == property.id }
                            }
                        }
                    )
                }
            }
            .padding(.vertical)
        }
        .refreshable {
            await loadProperties()
        }
    }
    
    private func loadProperties() async {
        print("📱 HomeView: Starting to load properties")
        viewModel.isLoading = true
        viewModel.error = nil
        
        do {
            print("📱 HomeView: Calling NetworkService.fetchHouses()")
            properties = try await NetworkService.shared.fetchHouses()
            properties.forEach { stateManager.setInitialState(for: $0) }
            viewModel.isLoading = false
            print("📱 HomeView: Finished loading properties, isLoading set to false")
        } catch {
            print("❌ HomeView: Error loading properties: \(error)")
            print("❌ HomeView: Error Description: \(error.localizedDescription)")
            
            if let urlError = error as? URLError,
               urlError.code == .userAuthenticationRequired {
                print("🔐 HomeView: Authentication required, attempting to refresh token")
                
                // Prevent multiple simultaneous refresh attempts
                guard !isRefreshingToken else { return }
                isRefreshingToken = true
                
                do {
                    // Try to refresh the token
                    _ = try await authService.refreshToken()
                    
                    // Token refresh successful, retry loading properties
                    print("🔐 HomeView: Token refreshed successfully, retrying property load")
                    properties = try await NetworkService.shared.fetchHouses()
                    properties.forEach { stateManager.setInitialState(for: $0) }
                    viewModel.isLoading = false
                } catch {
                    print("❌ HomeView: Token refresh failed: \(error)")
                    // If token refresh fails, show login sheet
                    showingLoginSheet = true
                    viewModel.error = error
                }
                
                isRefreshingToken = false
            } else {
                viewModel.error = error
            }
            
            viewModel.isLoading = false
        }
    }
}

class HomeViewModel: ObservableObject {
    @Published var properties: [Property] = []
    @Published var isLoading = false
    @Published var error: Error?
}

// MARK: - Helper Views
struct LoadingView: View {
    var body: some View {
        VStack(spacing: 20) {
            ProgressView()
                .progressViewStyle(CircularProgressViewStyle(tint: Theme.Colors.primary))
                .scaleEffect(1.5)
            Text("Loading properties...")
                .foregroundColor(Theme.Colors.secondary)
        }
    }
}

struct ErrorView: View {
    let error: Error
    let onRetry: () -> Void
    
    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.largeTitle)
                .foregroundColor(.yellow)
            Text("Error loading properties")
                .font(.headline)
            Text(error.localizedDescription)
                .font(.subheadline)
                .foregroundColor(Theme.Colors.secondary)
            Button("Retry", action: onRetry)
                .padding()
                .glassBackground()
        }
        .padding()
    }
}

// Button style extension for animation
extension View {
    func filterButtonStyle() -> some View {
        self.buttonStyle(FilterButtonStyle())
    }
}

// Custom button style for filter button animation
struct FilterButtonStyle: ButtonStyle {
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.92 : 1.0)
            .brightness(configuration.isPressed ? 0.05 : 0)
            .opacity(configuration.isPressed ? 0.9 : 1.0)
            .animation(.spring(response: 0.3, dampingFraction: 0.6, blendDuration: 0.1), value: configuration.isPressed)
    }
}

struct HomeView_Previews: PreviewProvider {
    static var previews: some View {
        HomeView()
            .environmentObject(AuthenticationService())
    }
} 