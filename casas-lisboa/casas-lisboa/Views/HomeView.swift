import SwiftUI
import MessageUI

// MARK: - Navigation Bar View
struct CustomNavigationBar: View {
    let title: String
    let onFilterTap: () -> Void
    
    var body: some View {
        HStack {
            Text(title)
                .font(.title2)
                .fontWeight(.bold)
                .foregroundColor(Theme.Colors.primary)
            
            Spacer()
            
            Button(action: onFilterTap) {
                HStack(spacing: 6) {
                    Image(systemName: "line.3.horizontal.decrease")
                    Text("Filters")
                }
                .padding(.horizontal, 16)
                .padding(.vertical, 8)
                .glassBackground()
            }
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

// MARK: - Property List View
struct PropertyListView: View {
    let properties: [Property]
    let onFavoriteToggle: (Property) -> Void
    let onDelete: (Property) -> Void
    let onContactedChange: (Property) -> Void
    let onContactAgent: (Property) -> Void
    let onDiscard: (Property) -> Void
    
    var body: some View {
        ScrollView {
            LazyVStack(spacing: 0) {
                ForEach(properties) { property in
                    PropertyCardView(
                        property: property,
                        onFavoriteToggle: onFavoriteToggle,
                        onDelete: { onDelete($0) },
                        onContactedChange: { onContactedChange($0) },
                        onDiscard: { onDiscard($0) }
                    )
                    .transition(.opacity.combined(with: .move(edge: .leading)))
                }
            }
            .padding(.bottom, 80)
        }
        .scrollIndicators(.hidden)
        .animation(Theme.Animation.spring, value: properties)
    }
}

// MARK: - Home View
struct HomeView: View {
    @StateObject private var filterOptions = FilterOptions()
    @State private var properties: [Property] = []
    @State private var showFilterSheet = false
    @State private var selectedProperty: Property?
    @State private var showContactSheet = false
    @State private var searchText = ""
    @State private var isLoading = false
    @State private var error: Error?
    
    var filteredProperties: [Property] {
        filterOptions.filterProperties(properties)
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Theme.Colors.background.edgesIgnoringSafeArea(.all)
                
                VStack(spacing: 0) {
                    CustomNavigationBar(
                        title: "Lisbon Rentals",
                        onFilterTap: { 
                            Theme.Haptics.impact(style: .light)
                            showFilterSheet = true 
                        }
                    )
                    
                    if isLoading {
                        Spacer()
                        ProgressView()
                            .tint(.white)
                        Spacer()
                    } else if let error = error {
                        Spacer()
                        VStack(spacing: 16) {
                            Image(systemName: "exclamationmark.triangle")
                                .font(.largeTitle)
                                .foregroundColor(.yellow)
                            Text("Error loading properties")
                                .font(.headline)
                            Text(error.localizedDescription)
                                .font(.subheadline)
                                .foregroundColor(Theme.Colors.secondary)
                            Button("Retry") {
                                Task {
                                    await loadProperties()
                                }
                            }
                            .padding()
                            .glassBackground()
                        }
                        .padding()
                        Spacer()
                    } else {
                        ScrollView(.vertical, showsIndicators: false) {
                            LazyVStack(spacing: 0) {
                                ForEach(filteredProperties) { property in
                                    PropertyCardView(
                                        property: property,
                                        onFavoriteToggle: { updatedProperty in
                                            if let index = properties.firstIndex(where: { $0.id == updatedProperty.id }) {
                                                properties[index].isFavorite = updatedProperty.isFavorite
                                            }
                                        },
                                        onDelete: { property in
                                            withAnimation {
                                                properties.removeAll { $0.id == property.id }
                                            }
                                        },
                                        onContactedChange: { updatedProperty in
                                            if let index = properties.firstIndex(where: { $0.id == updatedProperty.id }) {
                                                properties[index].contacted = updatedProperty.contacted
                                            }
                                        },
                                        onDiscard: { property in
                                            Task {
                                                do {
                                                    try await NetworkService.shared.toggleDiscarded(for: property.houseId)
                                                    if let index = properties.firstIndex(where: { $0.id == property.id }) {
                                                        properties[index].discarded = true
                                                        withAnimation {
                                                            properties.removeAll { $0.id == property.id }
                                                        }
                                                    }
                                                } catch {
                                                    print("❌ Failed to discard property: \(error.localizedDescription)")
                                                }
                                            }
                                        }
                                    )
                                    .transition(.opacity.combined(with: .move(edge: .leading)))
                                }
                            }
                            .padding(.bottom, 20)
                        }
                    }
                }
            }
        }
        .accentColor(Theme.Colors.primary)
        .preferredColorScheme(.dark)
        .filterSheet(isPresented: $showFilterSheet, filterOptions: filterOptions)
        .sheet(isPresented: $showContactSheet, content: {
            if let property = selectedProperty {
                ContactOptionsSheet(property: property)
            }
        })
        .task {
            await loadProperties()
        }
    }
    
    private func loadProperties() async {
        print("📱 HomeView: Starting to load properties")
        isLoading = true
        error = nil
        
        do {
            print("📱 HomeView: Calling NetworkService.fetchHouses()")
            properties = try await NetworkService.shared.fetchHouses()
            print("📱 HomeView: Successfully loaded \(properties.count) properties")
        } catch {
            print("❌ HomeView: Error loading properties: \(error)")
            print("❌ HomeView: Error Description: \(error.localizedDescription)")
            self.error = error
        }
        
        print("📱 HomeView: Finished loading properties, isLoading set to false")
        isLoading = false
    }
}

#Preview {
    HomeView()
} 