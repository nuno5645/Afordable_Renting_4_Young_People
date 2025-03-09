import SwiftUI

struct FavoritesView: View {
    @State private var properties: [Property] = []
    
    var body: some View {
        NavigationStack {
            ZStack {
                Theme.Colors.background.edgesIgnoringSafeArea(.all)
                
                if properties.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "heart.slash")
                            .font(.system(size: 60))
                            .foregroundColor(Theme.Colors.secondary)
                        Text("No Favorites Yet")
                            .font(.title2)
                            .fontWeight(.semibold)
                        Text("Properties you favorite will appear here")
                            .font(.subheadline)
                            .foregroundColor(Theme.Colors.secondary)
                    }
                } else {
                    PropertyListView(
                        properties: properties,
                        onFavoriteToggle: { property in
                            if let index = properties.firstIndex(where: { $0.id == property.id }) {
                                properties.remove(at: index)
                            }
                        },
                        onDelete: { property in
                            properties.removeAll { $0.id == property.id }
                        },
                        onContactedChange: { property in
                            if let index = properties.firstIndex(where: { $0.id == property.id }) {
                                properties[index].contacted = property.contacted
                            }
                        },
                        onContactAgent: { _ in },
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
                }
            }
            .navigationTitle("Favorites")
        }
    }
}

#Preview {
    FavoritesView()
        .preferredColorScheme(.dark)
} 