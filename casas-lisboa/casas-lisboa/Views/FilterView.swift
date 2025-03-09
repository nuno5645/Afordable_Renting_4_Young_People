import SwiftUI

struct FilterView: View {
    @Binding var isPresented: Bool
    @Binding var isExpanded: Bool
    @ObservedObject var filterOptions: FilterOptions
    
    var body: some View {
        VStack(spacing: 0) {
            // Top handle bar with modern design
            VStack(spacing: 8) {
                Rectangle()
                    .fill(Theme.Colors.glassBorder)
                    .frame(width: 36, height: 4)
                    .cornerRadius(2)
            }
            .frame(maxWidth: .infinity)
            .padding(.top, 12)
            .padding(.bottom, 4)
            
            ScrollView(showsIndicators: false) {
                VStack(alignment: .leading, spacing: 24) {
                    // Expand/Collapse button
                    Button(action: {
                        Theme.Haptics.impact(style: .light)
                        withAnimation(Theme.Animation.spring) {
                            isExpanded.toggle()
                        }
                    }) {
                        HStack(spacing: 4) {
                            Image(systemName: "chevron.down")
                                .font(.system(size: 16, weight: .medium))
                                .rotationEffect(.degrees(isExpanded ? 180 : 0))
                            Text(isExpanded ? "Collapse" : "Expand")
                                .font(.system(size: 14))
                        }
                        .foregroundColor(Theme.Colors.primary.opacity(0.6))
                        .padding(.vertical, 8)
                        .padding(.horizontal, 16)
                        .glassBackground()
                        .frame(maxWidth: .infinity)
                    }
                    .padding(.top, 8)
                    .padding(.bottom, 8)
                    
                    // Sort options
                    FilterSection(title: "Sort By") {
                        VStack(spacing: Theme.Layout.spacing) {
                            FilterButton(
                                title: "Price",
                                icon: "arrow.up.arrow.down",
                                isSelected: filterOptions.sortBy == .price
                            ) {
                                withAnimation {
                                    filterOptions.sortBy = .price
                                    filterOptions.sortAscending.toggle()
                                }
                            }
                            
                            FilterButton(
                                title: "Area",
                                icon: "square.fill",
                                isSelected: filterOptions.sortBy == .area
                            ) {
                                withAnimation {
                                    filterOptions.sortBy = .area
                                    filterOptions.sortAscending.toggle()
                                }
                            }
                            
                            FilterButton(
                                title: "Bedrooms",
                                icon: "bed.double.fill",
                                isSelected: filterOptions.sortBy == .bedrooms
                            ) {
                                withAnimation {
                                    filterOptions.sortBy = .bedrooms
                                    filterOptions.sortAscending.toggle()
                                }
                            }
                        }
                    }
                    
                    if isExpanded {
                        // Price range slider
                        FilterSection(title: "Price Range: €\(Int(filterOptions.priceRange))") {
                            VStack(spacing: Theme.Layout.spacing) {
                                Slider(value: $filterOptions.priceRange,
                                       in: filterOptions.minPrice...filterOptions.maxPrice,
                                       step: 50)
                                    .tint(Theme.Colors.primary)
                                
                                HStack {
                                    Text("€\(Int(filterOptions.minPrice))")
                                        .font(.caption)
                                        .foregroundColor(Theme.Colors.secondary)
                                    
                                    Spacer()
                                    
                                    Text("€\(Int(filterOptions.maxPrice))")
                                        .font(.caption)
                                        .foregroundColor(Theme.Colors.secondary)
                                }
                            }
                            .padding()
                            .glassBackground()
                        }
                        .transition(.opacity.combined(with: .move(edge: .top)))
                        
                        // Property type selection
                        FilterSection(title: "Property Type") {
                            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())],
                                    spacing: Theme.Layout.spacing) {
                                ForEach(PropertyType.allCases, id: \.self) { type in
                                    FilterChip(
                                        title: type.rawValue,
                                        isSelected: filterOptions.selectedPropertyTypes.contains(type)
                                    ) {
                                        Theme.Haptics.impact(style: .light)
                                        withAnimation {
                                            if filterOptions.selectedPropertyTypes.contains(type) {
                                                filterOptions.selectedPropertyTypes.remove(type)
                                            } else {
                                                filterOptions.selectedPropertyTypes.insert(type)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        .transition(.opacity.combined(with: .move(edge: .top)))
                        
                        // Source selection
                        FilterSection(title: "Source") {
                            LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())],
                                    spacing: Theme.Layout.spacing) {
                                ForEach(PropertySource.allCases, id: \.self) { source in
                                    FilterChip(
                                        title: source.rawValue,
                                        isSelected: filterOptions.selectedSources.contains(source)
                                    ) {
                                        Theme.Haptics.impact(style: .light)
                                        withAnimation {
                                            if filterOptions.selectedSources.contains(source) {
                                                filterOptions.selectedSources.remove(source)
                                            } else {
                                                filterOptions.selectedSources.insert(source)
                                            }
                                        }
                                    }
                                }
                            }
                        }
                        .transition(.opacity.combined(with: .move(edge: .top)))
                    }
                }
                .padding(.horizontal)
                .padding(.bottom, 100)
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .background(Theme.Colors.background)
        .preferredColorScheme(.dark)
    }
}

// MARK: - Helper Views
struct FilterSection<Content: View>: View {
    let title: String
    let content: Content
    
    init(title: String, @ViewBuilder content: () -> Content) {
        self.title = title
        self.content = content()
    }
    
    var body: some View {
        VStack(alignment: .leading, spacing: Theme.Layout.spacing) {
            Text(title)
                .font(.headline)
                .foregroundColor(Theme.Colors.secondary)
            content
        }
    }
}

struct FilterButton: View {
    let title: String
    let icon: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: {
            Theme.Haptics.impact(style: .light)
            action()
        }) {
            HStack {
                Text(title)
                    .foregroundColor(Theme.Colors.primary)
                Spacer()
                Image(systemName: icon)
                    .font(.caption)
                    .foregroundColor(isSelected ? Theme.Colors.primary : Theme.Colors.secondary)
            }
            .padding()
            .glassBackground()
        }
    }
}

struct FilterChip: View {
    let title: String
    let isSelected: Bool
    let action: () -> Void
    
    var body: some View {
        Button(action: action) {
            Text(title)
                .frame(maxWidth: .infinity)
                .padding()
                .background(isSelected ? Theme.Colors.primary.opacity(0.2) : Theme.Colors.glassBackground)
                .foregroundColor(isSelected ? Theme.Colors.primary : Theme.Colors.secondary)
                .cornerRadius(Theme.Layout.cornerRadius)
                .overlay(
                    RoundedRectangle(cornerRadius: Theme.Layout.cornerRadius)
                        .stroke(
                            isSelected ? Theme.Colors.primary : Theme.Colors.glassBorder,
                            lineWidth: 0.5
                        )
                )
        }
    }
}

struct FilterViewModifier: ViewModifier {
    @Binding var isPresented: Bool
    var filterOptions: FilterOptions
    @State private var isExpanded = false
    
    func body(content: Content) -> some View {
        ZStack {
            content
            
            if isPresented {
                Color.black.opacity(0.4)
                    .ignoresSafeArea()
                    .onTapGesture {
                        withAnimation(Theme.Animation.spring) {
                            if isExpanded {
                                isExpanded = false
                            } else {
                                isPresented = false
                            }
                        }
                    }
                
                VStack {
                    Spacer()
                    
                    FilterView(isPresented: $isPresented, isExpanded: $isExpanded, filterOptions: filterOptions)
                        .frame(maxHeight: UIScreen.main.bounds.height * 0.85)
                        .frame(height: isExpanded ? UIScreen.main.bounds.height * 0.85 : UIScreen.main.bounds.height * 0.4)
                        .background(
                            Theme.Colors.surface
                                .cornerRadius(32, corners: [.topLeft, .topRight])
                        )
                        .transition(.move(edge: .bottom))
                }
                .ignoresSafeArea()
                .transition(.opacity)
                .animation(Theme.Animation.spring, value: isPresented)
                .animation(Theme.Animation.spring, value: isExpanded)
            }
        }
    }
}

extension View {
    func filterSheet(isPresented: Binding<Bool>, filterOptions: FilterOptions) -> some View {
        self.modifier(FilterViewModifier(isPresented: isPresented, filterOptions: filterOptions))
    }
}

// Helper for rounded corners
extension View {
    func cornerRadius(_ radius: CGFloat, corners: UIRectCorner) -> some View {
        clipShape(RoundedCorner(radius: radius, corners: corners))
    }
}

struct RoundedCorner: Shape {
    var radius: CGFloat = .infinity
    var corners: UIRectCorner = .allCorners
    
    func path(in rect: CGRect) -> Path {
        let path = UIBezierPath(roundedRect: rect, byRoundingCorners: corners, cornerRadii: CGSize(width: radius, height: radius))
        return Path(path.cgPath)
    }
}

#Preview {
    Color.gray
        .modifier(FilterViewModifier(isPresented: .constant(true), filterOptions: FilterOptions()))
} 