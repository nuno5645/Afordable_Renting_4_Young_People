import SwiftUI
import SwiftUIX

struct SearchView: View {
    @State private var searchText = ""
    @State private var properties: [Property] = []
    @State private var isSearching = false
    @FocusState private var isSearchFocused: Bool
    
    var filteredProperties: [Property] {
        if searchText.isEmpty {
            return []
        }
        return properties.filter { property in
            property.location.localizedCaseInsensitiveContains(searchText) ||
            property.name.localizedCaseInsensitiveContains(searchText)
        }
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Theme.Colors.background.edgesIgnoringSafeArea(.all)
                
                VStack(spacing: 0) {
                    // Enhanced search bar with native SwiftUI
                    HStack {
                        Image(systemName: "magnifyingglass")
                            .foregroundColor(Theme.Colors.secondary)
                        
                        TextField("Search by location or name...", text: $searchText)
                            .textFieldStyle(.plain)
                            .focused($isSearchFocused)
                            .foregroundColor(Theme.Colors.primary)
                            .submitLabel(.search)
                            .onSubmit {
                                if !searchText.isEmpty {
                                    isSearching = true
                                }
                            }
                            .onTapGesture {
                                isSearchFocused = true
                            }
                        
                        if !searchText.isEmpty {
                            Button(action: {
                                searchText = ""
                            }) {
                                Image(systemName: "xmark.circle.fill")
                                    .foregroundColor(Theme.Colors.secondary)
                            }
                        }
                    }
                    .padding()
                    .glassBackground()
                    .padding(.horizontal)
                    .padding(.vertical, 8)
                    
                    if searchText.isEmpty {
                        VStack(spacing: 16) {
                            Image(systemName: "magnifyingglass")
                                .font(.system(size: 60))
                                .foregroundColor(Theme.Colors.secondary)
                            Text("Search Properties")
                                .font(.title2)
                                .fontWeight(.semibold)
                            Text("Enter a location or name to search")
                                .font(.subheadline)
                                .foregroundColor(Theme.Colors.secondary)
                        }
                        .frame(maxHeight: .infinity)
                    } else {
                        if isSearching {
                            ActivityIndicator()
                                .animated(true)
                                .style(.large)
                                .tintColor(.white)
                                .frame(maxHeight: .infinity)
                        } else {
                            if filteredProperties.isEmpty {
                                VStack(spacing: 16) {
                                    Image(systemName: "magnifyingglass.circle")
                                        .font(.system(size: 60))
                                        .foregroundColor(Theme.Colors.secondary)
                                    Text("No Results Found")
                                        .font(.title2)
                                        .fontWeight(.semibold)
                                    Text("Try adjusting your search terms")
                                        .font(.subheadline)
                                        .foregroundColor(Theme.Colors.secondary)
                                }
                                .frame(maxHeight: .infinity)
                            } else {
                                PropertyListView(
                                    properties: filteredProperties,
                                    onFavoriteToggle: { property in
                                        if let index = properties.firstIndex(where: { $0.id == property.id }) {
                                            properties[index].isFavorite = property.isFavorite
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
                    }
                }
            }
            .navigationTitle("Search")
        }
        .task(id: searchText) {
            guard !searchText.isEmpty else {
                isSearching = false
                return
            }
            
            do {
                isSearching = true
                // Add debounce using SwiftUIX
                try await Task.sleep(nanoseconds: 500_000_000)
                properties = try await NetworkService.shared.fetchHouses()
                isSearching = false
            } catch {
                print("Search error: \(error)")
                isSearching = false
            }
        }
    }
}

#Preview {
    SearchView()
        .preferredColorScheme(.dark)
} 