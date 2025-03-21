import SwiftUI

struct FavoritesView: View {
    @State private var properties: [Property] = []
    @State private var isLoading = false
    @StateObject private var stateManager = PropertyStateManager.shared
    
    var body: some View {
        NavigationStack {
            ZStack {
                Theme.Colors.background.edgesIgnoringSafeArea(.all)
                
                if isLoading {
                    ProgressView()
                        .tint(.white)
                } else if properties.isEmpty {
                    VStack(spacing: 16) {
                        Image(systemName: "heart.slash")
                            .font(.system(size: 48))
                            .foregroundColor(Theme.Colors.secondary)
                        
                        Text("No Favorites Yet")
                            .font(.title2)
                            .foregroundColor(Theme.Colors.secondary)
                    }
                } else {
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            ForEach(properties) { property in
                                PropertyCardView(
                                    property: property,
                                    onFavoriteToggle: { updatedProperty in
                                        Task {
                                            do {
                                                try await NetworkService.shared.toggleFavorite(for: updatedProperty.houseId)
                                                withAnimation {
                                                    if let index = properties.firstIndex(where: { $0.id == updatedProperty.id }) {
                                                        properties.remove(at: index)
                                                    }
                                                }
                                            } catch {
                                                print("❌ Failed to toggle favorite: \(error.localizedDescription)")
                                                // Revert the state if the API call fails
                                                stateManager.toggleFavorite(updatedProperty.houseId)
                                            }
                                        }
                                    },
                                    onDelete: { property in
                                        withAnimation {
                                            properties.removeAll { $0.id == property.id }
                                        }
                                    },
                                    onContactedChange: { property in
                                        if let index = properties.firstIndex(where: { $0.id == property.id }) {
                                            properties[index].contacted = property.contacted
                                        }
                                    },
                                    onDiscard: { property in
                                        Task {
                                            do {
                                                try await NetworkService.shared.toggleDiscarded(for: property.houseId)
                                                withAnimation {
                                                    if let index = properties.firstIndex(where: { $0.id == property.id }) {
                                                        properties.remove(at: index)
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
                        .padding(.bottom, 20)
                    }
                }
            }
            .navigationTitle("Favorites")
        }
        .task {
            await loadFavorites()
        }
    }
    
    private func loadFavorites() async {
        isLoading = true
        do {
            let allProperties = try await NetworkService.shared.fetchHouses()
            allProperties.forEach { stateManager.setInitialState(for: $0) }
            withAnimation {
                properties = allProperties.filter { $0.isFavorite }
            }
        } catch {
            print("Failed to load favorites: \(error)")
        }
        isLoading = false
    }
}

#Preview {
    FavoritesView()
        .preferredColorScheme(.dark)
} 