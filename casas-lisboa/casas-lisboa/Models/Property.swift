import Foundation

struct Property: Identifiable, Equatable {
    let id: UUID
    let houseId: String
    let price: Int
    let location: String
    let bedrooms: Int
    let area: Double
    let areaStr: String
    let source: String
    let hasPhoto: Bool
    var isFavorite: Bool
    var contacted: Bool
    var discarded: Bool
    let name: String
    let imageUrls: [String]
    let url: String
    let scrapedAt: Date
    
    // Computed property for formatted price
    var formattedPrice: String {
        return "€\(price)/month"
    }
    
    // Computed property for formatted area
    var formattedArea: String {
        if !areaStr.isEmpty && areaStr != "0" {
            // If areaStr already contains m², return it as is
            if areaStr.contains("m²") {
                return areaStr
            }
            // Otherwise add m² to it
            return "\(areaStr) m²"
        }
        
        // If areaStr is empty, "0", or area is 0, return empty string
        if areaStr.isEmpty || areaStr == "0" || area == 0 {
            return ""
        }
        
        // Format numeric area with m²
        return String(format: "%.0f m²", area)
    }
    
    // Computed property for formatted scraped date
    var formattedScrapedDate: String {
        let formatter = RelativeDateTimeFormatter()
        formatter.unitsStyle = .full
        return formatter.localizedString(for: scrapedAt, relativeTo: Date())
    }
    
    // Implement Equatable
    static func == (lhs: Property, rhs: Property) -> Bool {
        return lhs.id == rhs.id
    }
}

// Mock data for development and previews
extension Property {
    static let mockProperties = [
        Property(
            id: UUID(),
            houseId: "mock-1",
            price: 700,
            location: "N/A, Odivelas",
            bedrooms: 1,
            area: 0.0,
            areaStr: "N/A",
            source: "Casa SAPO",
            hasPhoto: false,
            isFavorite: false,
            contacted: false,
            discarded: false,
            name: "Apartamento T1",
            imageUrls: [],
            url: "",
            scrapedAt: Date()
        ),
        Property(
            id: UUID(),
            houseId: "mock-2",
            price: 850,
            location: "Benfica, Lisboa",
            bedrooms: 1,
            area: 45.0,
            areaStr: "45 m²",
            source: "Idealista",
            hasPhoto: false,
            isFavorite: false,
            contacted: false,
            discarded: false,
            name: "Apartamento T1",
            imageUrls: [],
            url: "",
            scrapedAt: Date().addingTimeInterval(-3600) // 1 hour ago
        )
    ]
} 