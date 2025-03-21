import SwiftUI

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
                    PropertyCardContainer(
                        property: property,
                        onPropertyUpdate: { updatedProperty in
                            if updatedProperty.isFavorite != property.isFavorite {
                                onFavoriteToggle(updatedProperty)
                            }
                            if updatedProperty.contacted != property.contacted {
                                onContactedChange(updatedProperty)
                            }
                        },
                        onPropertyRemove: { property in
                            onDiscard(property)
                        }
                    )
                }
            }
            .padding(.bottom, 20)
        }
    }
}

#Preview {
    PropertyListView(
        properties: Property.mockProperties,
        onFavoriteToggle: { _ in },
        onDelete: { _ in },
        onContactedChange: { _ in },
        onContactAgent: { _ in },
        onDiscard: { _ in }
    )
    .preferredColorScheme(.dark)
} 