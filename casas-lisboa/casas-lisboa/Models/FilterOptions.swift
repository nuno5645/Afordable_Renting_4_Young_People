import Foundation

enum SortOption: String, CaseIterable {
    case price = "Price"
    case area = "Area"
    case bedrooms = "Bedrooms"
}

enum PropertyType: String, CaseIterable {
    case studio = "Studio"
    case oneBedroom = "1 Bedroom"
    case twoBedrooms = "2 Bedrooms"
    case threePlusBedrooms = "3+ Bedrooms"
}

enum PropertySource: String, CaseIterable {
    case era = "ERA"
    case idealista = "Idealista"
    case imovirtual = "Imovirtual"
    case casaSapo = "Casa SAPO"
}

class FilterOptions: ObservableObject {
    @Published var sortBy: SortOption = .price
    @Published var sortAscending: Bool = true
    @Published var priceRange: Double = 1500
    @Published var selectedPropertyTypes: Set<PropertyType> = []
    @Published var selectedSources: Set<PropertySource> = []
    
    // Computed properties for min and max price
    let minPrice: Double = 500
    let maxPrice: Double = 3000
    
    // Filter properties based on current filter options
    func filterProperties(_ properties: [Property]) -> [Property] {
        var filteredProperties = properties
        
        // Filter by price
        filteredProperties = filteredProperties.filter { $0.price <= Int(priceRange) }
        
        // Filter by property type (bedrooms)
        if !selectedPropertyTypes.isEmpty {
            filteredProperties = filteredProperties.filter { property in
                if selectedPropertyTypes.contains(.studio) && property.bedrooms == 0 {
                    return true
                }
                if selectedPropertyTypes.contains(.oneBedroom) && property.bedrooms == 1 {
                    return true
                }
                if selectedPropertyTypes.contains(.twoBedrooms) && property.bedrooms == 2 {
                    return true
                }
                if selectedPropertyTypes.contains(.threePlusBedrooms) && property.bedrooms >= 3 {
                    return true
                }
                return false
            }
        }
        
        // Filter by source
        if !selectedSources.isEmpty {
            filteredProperties = filteredProperties.filter { property in
                for source in selectedSources {
                    if property.source == source.rawValue {
                        return true
                    }
                }
                return false
            }
        }
        
        // Sort properties
        filteredProperties.sort { first, second in
            switch sortBy {
            case .price:
                return sortAscending ? first.price < second.price : first.price > second.price
            case .area:
                return sortAscending ? first.area < second.area : first.area > second.area
            case .bedrooms:
                return sortAscending ? first.bedrooms < second.bedrooms : first.bedrooms > second.bedrooms
            }
        }
        
        return filteredProperties
    }
} 