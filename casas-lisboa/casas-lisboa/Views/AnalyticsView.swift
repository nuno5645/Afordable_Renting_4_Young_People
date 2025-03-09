import SwiftUI

struct AnalyticsView: View {
    @State private var properties: [Property] = []
    @State private var isLoading = false
    
    // Break down calculations into separate functions
    private func calculateAveragePrice() -> Double {
        guard !properties.isEmpty else { return 0 }
        let total = properties.reduce(0) { $0 + $1.price }
        return Double(total) / Double(properties.count)
    }
    
    private func calculateAverageArea() -> Double {
        guard !properties.isEmpty else { return 0 }
        let total = properties.reduce(0) { $0 + ($1.area ?? 0) }
        return Double(total) / Double(properties.count)
    }
    
    private func calculatePricePerSquareMeter() -> Double {
        let avgArea = calculateAverageArea()
        guard avgArea > 0 else { return 0 }
        return calculateAveragePrice() / avgArea
    }
    
    private func countPropertiesByBedrooms(_ bedrooms: Int) -> Int {
        if bedrooms == 3 {
            return properties.filter { $0.bedrooms >= 3 }.count
        }
        return properties.filter { $0.bedrooms == bedrooms }.count
    }
    
    private var propertyCategories: [(title: String, bedrooms: Int)] {
        [
            ("Studio", 0),
            ("1 Bedroom", 1),
            ("2 Bedrooms", 2),
            ("3+ Bedrooms", 3)
        ]
    }
    
    var body: some View {
        NavigationStack {
            ZStack {
                Theme.Colors.background.edgesIgnoringSafeArea(.all)
                
                if isLoading {
                    ProgressView()
                        .tint(Theme.Colors.primary)
                } else {
                    ScrollView {
                        VStack(spacing: 16) {
                            // Price Statistics
                            StatisticCard(
                                title: "Price Statistics",
                                items: [
                                    StatItem(
                                        title: "Average Price",
                                        value: String(format: "€%.2f", calculateAveragePrice()),
                                        icon: "eurosign.circle.fill",
                                        valueSize: .large
                                    ),
                                    StatItem(
                                        title: "Price/m²",
                                        value: String(format: "€%.2f/m²", calculatePricePerSquareMeter()),
                                        icon: "chart.line.uptrend.xyaxis",
                                        valueSize: .large
                                    )
                                ]
                            )
                            
                            // Property Statistics
                            StatisticCard(
                                title: "Property Statistics",
                                items: [
                                    StatItem(
                                        title: "Total Properties",
                                        value: "\(properties.count)",
                                        icon: "house.fill",
                                        valueSize: .large
                                    ),
                                    StatItem(
                                        title: "Average Area",
                                        value: String(format: "%.1f m²", calculateAverageArea()),
                                        icon: "square.fill",
                                        valueSize: .large
                                    )
                                ]
                            )
                            
                            // Property Types Distribution
                            StatisticCard(
                                title: "Property Types",
                                items: propertyCategories.map { category in
                                    StatItem(
                                        title: category.title,
                                        value: "\(countPropertiesByBedrooms(category.bedrooms))",
                                        icon: "bed.double",
                                        valueSize: .medium
                                    )
                                }
                            )
                        }
                        .padding(.horizontal)
                        .padding(.top, 8)
                    }
                }
            }
            .navigationTitle("Analytics")
        }
        .task {
            await loadProperties()
        }
    }
    
    private func loadProperties() async {
        isLoading = true
        do {
            properties = try await NetworkService.shared.fetchHouses()
        } catch {
            print("Failed to load properties: \(error)")
        }
        isLoading = false
    }
}

struct StatItem: Identifiable {
    let id = UUID()
    let title: String
    let value: String
    let icon: String
    let valueSize: StatValueSize
}

enum StatValueSize {
    case medium
    case large
}

struct StatisticCard: View {
    let title: String
    let items: [StatItem]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(title)
                .font(.title3)
                .fontWeight(.semibold)
                .foregroundColor(.white)
                .padding(.horizontal, 16)
                .padding(.top, 16)
            
            VStack(spacing: 16) {
                ForEach(items) { item in
                    HStack(spacing: 16) {
                        Image(systemName: item.icon)
                            .font(.system(size: 20))
                            .foregroundColor(.white)
                            .frame(width: 24)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(item.title)
                                .font(.subheadline)
                                .foregroundColor(Theme.Colors.secondary)
                            Text(item.value)
                                .font(item.valueSize == .large ? .title2 : .title3)
                                .fontWeight(.semibold)
                                .foregroundColor(.white)
                        }
                        
                        Spacer()
                    }
                    .padding(.horizontal, 16)
                    
                    if item.id != items.last?.id {
                        Divider()
                            .background(Theme.Colors.secondary.opacity(0.2))
                    }
                }
            }
            .padding(.bottom, 16)
        }
        .background(Theme.Colors.surface)
        .cornerRadius(16)
    }
}

#Preview {
    AnalyticsView()
        .preferredColorScheme(.dark)
} 