import SwiftUI

// Add at the top level, before CachedAsyncImage
private let imageCache = NSCache<NSString, UIImage>()

struct CachedAsyncImage: View {
    let url: URL
    @State private var image: UIImage?
    
    var body: some View {
        Group {
            if let image = image {
                Image(uiImage: image)
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } else {
                Rectangle()
                    .fill(Theme.Colors.surface)
                    .overlay {
                        ProgressView()
                            .tint(.white)
                    }
            }
        }
        .onAppear {
            loadImage()
        }
    }
    
    private func loadImage() {
        // Check cache first
        if let cachedImage = imageCache.object(forKey: url.absoluteString as NSString) {
            self.image = cachedImage
            return
        }
        
        // Use NetworkService's session to handle SSL certificate validation
        if url.host == "100.95.208.157" {
            Task {
                do {
                    let (data, _) = try await NetworkService.shared.session.data(from: url)
                    if let loadedImage = UIImage(data: data) {
                        imageCache.setObject(loadedImage, forKey: url.absoluteString as NSString)
                        DispatchQueue.main.async {
                            self.image = loadedImage
                        }
                    }
                } catch {
                    print("❌ CachedAsyncImage: Failed to load image: \(error.localizedDescription)")
                }
            }
        } else {
            URLSession.shared.dataTask(with: url) { data, _, _ in
                if let data = data, let loadedImage = UIImage(data: data) {
                    imageCache.setObject(loadedImage, forKey: url.absoluteString as NSString)
                    DispatchQueue.main.async {
                        self.image = loadedImage
                    }
                }
            }.resume()
        }
    }
}

struct PropertyCardView: View {
    @State var property: Property
    var onFavoriteToggle: (Property) -> Void
    var onDelete: ((Property) -> Void)?
    var onContactedChange: ((Property) -> Void)?
    var onDiscard: ((Property) -> Void)?
    
    // Animation state
    @State private var isPressed = false
    @State private var showContactSheet = false
    @State private var currentImageIndex = 0
    @State private var isAnimating = false
    
    // Image preloading
    @State private var preloadedImages: [Int: UIImage] = [:]
    
    var body: some View {
        VStack(alignment: .leading, spacing: 0) {
            // Property image or placeholder
            ZStack {
                if !property.imageUrls.isEmpty, let url = URL(string: property.imageUrls[currentImageIndex]) {
                    if let preloadedImage = preloadedImages[currentImageIndex] {
                        Image(uiImage: preloadedImage)
                            .resizable()
                            .aspectRatio(contentMode: .fill)
                            .frame(height: 200)
                            .clipped()
                            .transition(.opacity)
                    } else {
                        CachedAsyncImage(url: url)
                            .frame(height: 200)
                            .clipped()
                            .transition(.opacity)
                    }
                } else {
                    Rectangle()
                        .fill(Theme.Colors.surface)
                        .frame(height: 200)
                        .overlay {
                            VStack(spacing: 8) {
                                Image(systemName: "photo.slash")
                                    .font(.system(size: 40))
                                    .foregroundColor(Theme.Colors.secondary)
                                
                                Text("No Photo Available")
                                    .font(.headline)
                                    .foregroundColor(Theme.Colors.secondary)
                            }
                        }
                }
                
                // Navigation arrows and favorite button overlay
                VStack {
                    // Top row with favorite button
                    HStack {
                        Spacer()
                        Button(action: {
                            property.isFavorite.toggle()
                            Theme.Haptics.impact(style: .light)
                            onFavoriteToggle(property)
                        }) {
                            Image(systemName: property.isFavorite ? "heart.fill" : "heart")
                                .font(.title2)
                                .foregroundColor(property.isFavorite ? .red : .white)
                                .frame(width: 44, height: 44)
                                .background(Color.black.opacity(0.3))
                                .clipShape(Circle())
                                .shadow(color: .black.opacity(0.3), radius: 4, x: 0, y: 2)
                        }
                        .padding()
                    }
                    
                    // Image navigation
                    if property.imageUrls.count > 1 {
                        HStack {
                            // Previous button
                            Button(action: {
                                guard !isAnimating else { return }
                                navigateImage(direction: -1)
                            }) {
                                Image(systemName: "chevron.left")
                                    .font(.title3)
                                    .fontWeight(.semibold)
                                    .foregroundColor(.white)
                                    .frame(width: 40, height: 40)
                                    .background(Color.black.opacity(0.3))
                                    .clipShape(Circle())
                            }
                            
                            Spacer()
                            
                            // Next button
                            Button(action: {
                                guard !isAnimating else { return }
                                navigateImage(direction: 1)
                            }) {
                                Image(systemName: "chevron.right")
                                    .font(.title3)
                                    .fontWeight(.semibold)
                                    .foregroundColor(.white)
                                    .frame(width: 40, height: 40)
                                    .background(Color.black.opacity(0.3))
                                    .clipShape(Circle())
                            }
                        }
                        .padding(.horizontal, 16)
                        
                        Spacer()
                        
                        // Image counter
                        Text("\(currentImageIndex + 1)/\(property.imageUrls.count)")
                            .font(.caption)
                            .foregroundColor(.white)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(Color.black.opacity(0.3))
                            .cornerRadius(12)
                            .padding(.bottom, 8)
                    }
                }
            }
            .background(Theme.Colors.surface)
            
            // Property details
            VStack(alignment: .leading, spacing: Theme.Layout.spacing) {
                // Location
                HStack {
                    Image(systemName: "mappin.circle.fill")
                        .foregroundColor(Theme.Colors.secondary)
                    Text(property.location)
                        .font(.subheadline)
                        .foregroundColor(Theme.Colors.secondary)
                }
                .padding(.top, Theme.Layout.spacing)
                
                // Price
                Text(property.formattedPrice)
                    .font(.title2)
                    .fontWeight(.bold)
                    .foregroundColor(Theme.Colors.primary)
                
                // Property specs
                HStack(spacing: 16) {
                    PropertySpec(icon: "bed.double.fill", text: "\(property.bedrooms)")
                    PropertySpec(icon: "square.fill", text: property.formattedArea)
                    Spacer()
                    Text(property.source)
                        .font(.caption)
                        .foregroundColor(Theme.Colors.secondary)
                }
                
                // Action buttons
                HStack(spacing: Theme.Layout.spacing) {
                    // Visit button
                    Button(action: {
                        if let url = URL(string: property.url) {
                            UIApplication.shared.open(url)
                        }
                    }) {
                        HStack {
                            Image(systemName: "arrow.forward.circle.fill")
                            Text("Visit")
                        }
                        .font(.subheadline)
                        .fontWeight(.medium)
                        .foregroundColor(.white)
                        .frame(maxWidth: .infinity)
                        .padding(.vertical, 12)
                        .glassBackground()
                    }
                    
                    // Contacted button
                    Button(action: {
                        property.contacted.toggle()
                        Theme.Haptics.impact()
                        onContactedChange?(property)
                    }) {
                        Image(systemName: property.contacted ? "checkmark.circle.fill" : "envelope.fill")
                            .font(.title3)
                            .foregroundColor(property.contacted ? Theme.Colors.primary : .white)
                            .frame(width: 44, height: 44)
                            .glassBackground()
                    }
                    
                    // Delete/Discard button
                    Button(action: {
                        withAnimation(Theme.Animation.spring) {
                            Theme.Haptics.notification(type: .success)
                            onDiscard?(property)
                        }
                    }) {
                        Image(systemName: "trash.fill")
                            .font(.title3)
                            .foregroundColor(.red)
                            .frame(width: 44, height: 44)
                            .glassBackground()
                    }
                }
                .padding(.top, 8)
            }
            .padding(.horizontal, Theme.Layout.padding)
            .padding(.bottom, Theme.Layout.padding)
        }
        .background(Theme.Colors.surface)
        .cornerRadius(Theme.Layout.cornerRadius)
        .shadow(color: Theme.Colors.primary.opacity(0.1), radius: 10, x: 0, y: 5)
        .scaleEffect(isPressed ? 0.98 : 1.0)
        .simultaneousGesture(
            LongPressGesture(minimumDuration: 0.1)
                .onChanged { _ in
                    withAnimation(Theme.Animation.easeOut) {
                        isPressed = true
                    }
                }
                .onEnded { _ in
                    withAnimation(Theme.Animation.easeOut) {
                        isPressed = false
                    }
                }
        )
        .padding(.horizontal, Theme.Layout.padding)
        .padding(.vertical, 8)
        .sheet(isPresented: $showContactSheet) {
            ContactOptionsSheet(property: property)
        }
        .onAppear {
            preloadImages()
        }
        .onChange(of: currentImageIndex) { _ in
            preloadAdjacentImages()
        }
    }
    
    private func preloadImages() {
        for (index, urlString) in property.imageUrls.enumerated() {
            guard let url = URL(string: urlString) else { continue }
            
            URLSession.shared.dataTask(with: url) { data, _, _ in
                if let data = data, let image = UIImage(data: data) {
                    DispatchQueue.main.async {
                        preloadedImages[index] = image
                    }
                }
            }.resume()
        }
    }
    
    private func preloadAdjacentImages() {
        let adjacentIndices = [
            (currentImageIndex - 1 + property.imageUrls.count) % property.imageUrls.count,
            (currentImageIndex + 1) % property.imageUrls.count
        ]
        
        for index in adjacentIndices {
            guard preloadedImages[index] == nil,
                  let url = URL(string: property.imageUrls[index]) else { continue }
            
            URLSession.shared.dataTask(with: url) { data, _, _ in
                if let data = data, let image = UIImage(data: data) {
                    DispatchQueue.main.async {
                        preloadedImages[index] = image
                    }
                }
            }.resume()
        }
    }
    
    private func navigateImage(direction: Int) {
        isAnimating = true
        Theme.Haptics.impact(style: .light)
        
        withAnimation(.easeInOut(duration: 0.3)) {
            currentImageIndex = (currentImageIndex + direction + property.imageUrls.count) % property.imageUrls.count
        }
        
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) {
            isAnimating = false
        }
    }
}

// MARK: - Helper Views
struct PropertySpec: View {
    let icon: String
    let text: String
    
    var body: some View {
        HStack(spacing: 4) {
            Image(systemName: icon)
                .foregroundColor(Theme.Colors.secondary)
            Text(text)
                .foregroundColor(Theme.Colors.secondary)
        }
    }
}

#Preview {
    PropertyCardView(
        property: Property.mockProperties[0],
        onFavoriteToggle: { _ in },
        onDelete: { _ in },
        onContactedChange: { _ in },
        onDiscard: { _ in }
    )
    .preferredColorScheme(.dark)
} 