import SwiftUI

// Notification for scrolling to top
extension Notification.Name {
    static let scrollHomeToTop = Notification.Name("scrollHomeToTop")
}

struct MainTabView: View {
    @State private var selectedTab = 0
    
    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
                .tag(0)
                .onTapGesture {
                    if selectedTab == 0 {
                        NotificationCenter.default.post(name: .scrollHomeToTop, object: nil)
                    }
                }
            
            FavoritesView()
                .tabItem {
                    Label("Favorites", systemImage: "heart")
                }
                .tag(1)
            
            SearchView()
                .tabItem {
                    Label("Search", systemImage: "magnifyingglass")
                }
                .tag(2)
            
            AnalyticsView()
                .tabItem {
                    Label("Analytics", systemImage: "chart.bar")
                }
                .tag(3)
            
            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person")
                }
                .tag(4)
        }
        .accentColor(Theme.Colors.primary)
        .preferredColorScheme(.dark)
    }
}

#Preview {
    MainTabView()
} 