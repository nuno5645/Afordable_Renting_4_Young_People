import SwiftUI
import SwiftUIX

struct Theme {
    // MARK: - Colors
    struct Colors {
        static let background = Color.black
        static let surface = Color(UIColor.systemGray6)
        static let surfaceHighlight = Color.white.opacity(0.05)
        static let primary = Color.white
        static let secondary = Color.gray
        static let accent = Color.blue
        
        // Gradients
        static let cardGradient = LinearGradient(
            gradient: Gradient(colors: [Color.black.opacity(0.7), Color.black.opacity(0.8)]),
            startPoint: .top,
            endPoint: .bottom
        )
        
        // Glass effect with SwiftUIX's blur capabilities
        static let glassBackground = Color.white.opacity(0.1)
        static let glassBorder = Color.white.opacity(0.2)
    }
    
    // MARK: - Animations
    struct Animation {
        static let spring = SwiftUI.Animation.spring(response: 0.2, dampingFraction: 0.7)
        static let easeOut = SwiftUI.Animation.easeOut(duration: 0.15)
        static let easeInOut = SwiftUI.Animation.easeInOut(duration: 0.2)
    }
    
    // MARK: - Haptics
    struct Haptics {
        static func impact(style: UIImpactFeedbackGenerator.FeedbackStyle = .medium) {
            let generator = UIImpactFeedbackGenerator(style: style)
            generator.impactOccurred()
        }
        
        static func notification(type: UINotificationFeedbackGenerator.FeedbackType) {
            let generator = UINotificationFeedbackGenerator()
            generator.notificationOccurred(type)
        }
    }
    
    // MARK: - Layout
    struct Layout {
        static let cornerRadius: CGFloat = 16
        static let padding: CGFloat = 16
        static let spacing: CGFloat = 12
    }
    
    // MARK: - Shadows
    struct Shadows {
        static let small = Shadow(color: .black.opacity(0.1), radius: 4, x: 0, y: 2)
        static let medium = Shadow(color: .black.opacity(0.15), radius: 8, x: 0, y: 4)
        static let large = Shadow(color: .black.opacity(0.2), radius: 16, x: 0, y: 8)
    }
}

// MARK: - View Modifiers
extension View {
    func glassBackground() -> some View {
        self.background(
            ZStack {
                if #available(iOS 14.0, *) {
                    VisualEffectBlurView(blurStyle: .systemThinMaterial)
                        .cornerRadius(Theme.Layout.cornerRadius)
                } else {
                    Rectangle()
                        .fill(Theme.Colors.glassBackground)
                        .cornerRadius(Theme.Layout.cornerRadius)
                }
                RoundedRectangle(cornerRadius: Theme.Layout.cornerRadius)
                    .stroke(Theme.Colors.glassBorder, lineWidth: 0.5)
            }
        )
    }
    
    func cardShadow() -> some View {
        self.shadow(
            color: Theme.Shadows.medium.color,
            radius: Theme.Shadows.medium.radius,
            x: Theme.Shadows.medium.x,
            y: Theme.Shadows.medium.y
        )
    }
}

// MARK: - Helper Structs
struct Shadow {
    let color: Color
    let radius: CGFloat
    let x: CGFloat
    let y: CGFloat
} 
