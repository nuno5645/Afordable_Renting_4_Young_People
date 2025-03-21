import Foundation

class PropertyStateManager: ObservableObject {
    static let shared = PropertyStateManager()
    
    @Published private var favoriteStates: [String: Bool] = [:]
    @Published private var contactedStates: [String: Bool] = [:]
    @Published private var discardedStates: [String: Bool] = [:]
    
    private init() {}
    
    func isFavorite(_ houseId: String) -> Bool {
        favoriteStates[houseId] ?? false
    }
    
    func isContacted(_ houseId: String) -> Bool {
        contactedStates[houseId] ?? false
    }
    
    func isDiscarded(_ houseId: String) -> Bool {
        discardedStates[houseId] ?? false
    }
    
    func setInitialState(for property: Property) {
        favoriteStates[property.houseId] = property.isFavorite
        contactedStates[property.houseId] = property.contacted
        discardedStates[property.houseId] = property.discarded
    }
    
    func toggleFavorite(_ houseId: String) {
        favoriteStates[houseId] = !(favoriteStates[houseId] ?? false)
    }
    
    func toggleContacted(_ houseId: String) {
        contactedStates[houseId] = !(contactedStates[houseId] ?? false)
    }
    
    func toggleDiscarded(_ houseId: String) {
        discardedStates[houseId] = !(discardedStates[houseId] ?? false)
    }
    
    func resetStates() {
        favoriteStates.removeAll()
        contactedStates.removeAll()
        discardedStates.removeAll()
    }
} 