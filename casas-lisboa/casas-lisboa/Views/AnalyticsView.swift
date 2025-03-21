import SwiftUI
import SwiftUIX

struct AnalyticsView: View {
    @State private var properties: [Property] = []
    @State private var isLoading = false
    @State private var isRunningScrapers = false
    @State private var error: Error?
    @State private var scraperStatus: ScraperStatusData?
    @State private var lastRunDate: Date?
    
    private var totalNewProperties: Int {
        scraperStatus?.main_run.new_houses ?? 0
    }
    
    private var totalProcessedProperties: Int {
        scraperStatus?.main_run.total_houses ?? 0
    }
    
    private var lastRunFormatted: String {
        guard let lastRunStr = scraperStatus?.main_run.last_run_date else {
            print("📅 AnalyticsView: No last_run_date available")
            return "Never"
        }
        
        print("📅 AnalyticsView: Processing last_run_date: \(lastRunStr)")
        
        let formatter = ISO8601DateFormatter()
        formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
        
        guard let date = formatter.date(from: lastRunStr) else {
            print("📅 AnalyticsView: Failed to parse date: \(lastRunStr)")
            return "Never"
        }
        
        print("📅 AnalyticsView: Successfully parsed date: \(date)")
        
        let now = Date()
        let timeInterval = now.timeIntervalSince(date)
        
        // If less than 1 hour, show minutes
        if timeInterval < 3600 {
            let minutes = Int(timeInterval / 60)
            if minutes == 0 {
                return "Just now"
            }
            return "\(minutes) minute\(minutes == 1 ? "" : "s") ago"
        }
        
        // If less than 24 hours, show hours
        if timeInterval < 86400 {
            let hours = Int(timeInterval / 3600)
            return "\(hours) hour\(hours == 1 ? "" : "s") ago"
        }
        
        // If less than 30 days, show days
        if timeInterval < 2592000 {
            let days = Int(timeInterval / 86400)
            return "\(days) day\(days == 1 ? "" : "s") ago"
        }
        
        // For older dates, use a date formatter
        let dateFormatter = DateFormatter()
        dateFormatter.dateStyle = .medium
        dateFormatter.timeStyle = .short
        return dateFormatter.string(from: date)
    }
    
    private var lastRunDuration: String {
        guard let startStr = scraperStatus?.main_run.start_time,
              let endStr = scraperStatus?.main_run.end_time,
              let startDate = ISO8601DateFormatter().date(from: startStr),
              let endDate = ISO8601DateFormatter().date(from: endStr) else {
            return "N/A"
        }
        
        let duration = endDate.timeIntervalSince(startDate)
        let minutes = Int(duration) / 60
        let seconds = Int(duration) % 60
        
        if minutes > 0 {
            return "\(minutes)m \(seconds)s"
        } else {
            return "\(seconds)s"
        }
    }
    
    // Break down calculations into separate functions
    private func calculateAveragePrice() -> Double {
        guard !properties.isEmpty else { return 0 }
        let total = properties.reduce(0) { $0 + Double($1.price) }
        return total / Double(properties.count)
    }
    
    private func formatPrice(_ price: Double) -> String {
        let formatter = NumberFormatter()
        formatter.numberStyle = .decimal
        formatter.maximumFractionDigits = 0
        formatter.groupingSeparator = ","
        return "€\(formatter.string(from: NSNumber(value: price)) ?? "0")"
    }
    
    private func calculateAverageArea() -> Double {
        guard !properties.isEmpty else { return 0 }
        
        // Filter out properties with empty or invalid area_str
        let propertiesWithArea = properties.filter { property in
            let areaStr = property.areaStr
            guard !areaStr.isEmpty else { return false }
            // Extract numeric value from string (e.g., "100 m²" -> "100")
            let numericStr = areaStr.components(separatedBy: CharacterSet.decimalDigits.inverted)
                                  .joined()
            return Double(numericStr) ?? 0 > 0
        }
        
        guard !propertiesWithArea.isEmpty else { return 0 }
        
        let total = propertiesWithArea.reduce(0.0) { sum, property in
            let areaStr = property.areaStr
            // Extract numeric value from string
            let numericStr = areaStr.components(separatedBy: CharacterSet.decimalDigits.inverted)
                                  .joined()
            return sum + (Double(numericStr) ?? 0)
        }
        
        return total / Double(propertiesWithArea.count)
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
                    ActivityIndicator()
                        .animated(true)
                        .style(.large)
                        .tintColor(.white)
                } else {
                    ScrollView {
                        VStack(spacing: 16) {
                            // Run Scrapers Button with enhanced feedback
                            Button(action: {
                                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                                    runScrapers()
                                }
                            }) {
                                HStack(spacing: 12) {
                                    Image(systemName: "arrow.triangle.2.circlepath")
                                        .font(.system(size: 20))
                                        .symbolEffect(
                                            .bounce,
                                            options: .repeating,
                                            value: isRunningScrapers
                                        )
                                    Text(isRunningScrapers ? "Running..." : "Start Scrapers")
                                        .font(.headline)
                                }
                                .frame(maxWidth: .infinity)
                                .padding(.vertical, 12)
                                .background(
                                    RoundedRectangle(cornerRadius: 12)
                                        .fill(isRunningScrapers ? Theme.Colors.surface.opacity(0.5) : Theme.Colors.surface)
                                        .overlay(
                                            RoundedRectangle(cornerRadius: 12)
                                                .stroke(Theme.Colors.primary, lineWidth: 1)
                                                .opacity(isRunningScrapers ? 0.5 : 1)
                                        )
                                )
                                .foregroundColor(isRunningScrapers ? Theme.Colors.primary.opacity(0.5) : Theme.Colors.primary)
                            }
                            .buttonStyle(ScraperButtonStyle())
                            .pressAnimation()
                            .disabled(isRunningScrapers)
                            .padding(.horizontal)
                            
                            // Cards with staggered animations
                            Group {
                                // Scraper Status Card
                                StatisticCard(title: "Scraper Status", items: [
                                    StatItem(
                                        title: "Status",
                                        value: scraperStatus?.main_run.status.capitalized ?? "Unknown",
                                        icon: "arrow.triangle.2.circlepath",
                                        valueSize: .medium,
                                        showLoadingIndicator: scraperStatus?.main_run.status == "running"
                                    ),
                                    StatItem(
                                        title: "Last Run",
                                        value: lastRunFormatted,
                                        icon: "clock.fill",
                                        valueSize: .medium
                                    ),
                                    StatItem(
                                        title: "Run Duration",
                                        value: lastRunDuration,
                                        icon: "timer",
                                        valueSize: .medium
                                    ),
                                    StatItem(
                                        title: "New Properties",
                                        value: "\(totalNewProperties)",
                                        icon: "plus.circle.fill",
                                        valueSize: .medium
                                    )
                                ])
                                .transition(.moveAndFade)
                                .pressAnimation()
                                
                                // Individual Scraper Status
                                if let scrapers = scraperStatus?.scrapers, !scrapers.isEmpty {
                                    StatisticCard(
                                        title: "Scrapers Detail",
                                        items: scrapers.map { key, status in
                                            StatItem(
                                                title: status.name,
                                                value: "\(status.houses_found) new / \(status.houses_processed) total",
                                                icon: status.status == "running" ? "arrow.triangle.2.circlepath" : 
                                                      status.status == "completed" ? "checkmark.circle.fill" :
                                                      status.status == "failed" ? "xmark.circle.fill" : "clock.fill",
                                                valueSize: .medium,
                                                showLoadingIndicator: status.status == "running"
                                            )
                                        }
                                    )
                                    .transition(.moveAndFade)
                                    .pressAnimation()
                                }
                                
                                // Price Statistics
                                StatisticCard(
                                    title: "Price Statistics",
                                    items: [
                                        StatItem(
                                            title: "Average Price",
                                            value: formatPrice(calculateAveragePrice()),
                                            icon: "eurosign.circle.fill",
                                            valueSize: .large
                                        ),
                                        StatItem(
                                            title: "Price/m²",
                                            value: formatPrice(calculatePricePerSquareMeter()) + "/m²",
                                            icon: "chart.line.uptrend.xyaxis",
                                            valueSize: .large
                                        )
                                    ]
                                )
                                .transition(.moveAndFade)
                                .pressAnimation()
                                
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
                                .transition(.moveAndFade)
                                .pressAnimation()
                                
                                // Property Types
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
                                .transition(.moveAndFade)
                                .pressAnimation()
                            }
                            .padding(.horizontal)
                        }
                        .padding(.top, 8)
                    }
                    .scrollDismissesKeyboard(.immediately)
                    .scrollIndicators(.hidden)
                    .refreshable {
                        await loadProperties()
                        await loadScraperStatus()
                    }
                }
            }
            .navigationTitle("Analytics")
            .navigationBarTitleDisplayMode(.large)
        }
        .task {
            await loadProperties()
            await loadScraperStatus()
        }
    }
    
    private func loadProperties() async {
        isLoading = true
        do {
            properties = try await NetworkService.shared.fetchHouses()
        } catch {
            print("Failed to load properties: \(error)")
            self.error = error
        }
        withAnimation {
            isLoading = false
        }
    }
    
    private func loadScraperStatus() async {
        do {
            let status = try await NetworkService.shared.fetchScraperStatus()
            scraperStatus = status
            isRunningScrapers = status.main_run.status == "running"
        } catch {
            print("Failed to load scraper status: \(error)")
            self.error = error
        }
        isLoading = false
    }
    
    private func runScrapers() {
        print("📱 AnalyticsView: runScrapers called")
        guard !isRunningScrapers else { 
            print("📱 AnalyticsView: Scrapers already running, ignoring call")
            return 
        }
        
        Task {
            do {
                // Set initial running state with animation
                withAnimation(.spring(response: 0.3, dampingFraction: 0.7)) {
                    isRunningScrapers = true
                    // Create new status with running state
                    if let currentStatus = scraperStatus {
                        // Create new main run status
                        let newMainRun = MainRunStatus(
                            status: "running",
                            start_time: ISO8601DateFormatter().string(from: Date()),
                            end_time: nil,
                            total_houses: 0,
                            new_houses: 0,
                            error_message: nil,
                            last_run_date: currentStatus.main_run.last_run_date
                        )
                        
                        // Create new scraper statuses
                        var newScrapers: [String: ScraperStatusResponse] = [:]
                        for (key, scraper) in currentStatus.scrapers {
                            newScrapers[key] = ScraperStatusResponse(
                                name: scraper.name,
                                status: "running",
                                timestamp: ISO8601DateFormatter().string(from: Date()),
                                houses_processed: 0,
                                houses_found: 0,
                                error_message: nil
                            )
                        }
                        
                        // Create new scraper status data
                        scraperStatus = ScraperStatusData(
                            main_run: newMainRun,
                            scrapers: newScrapers
                        )
                    }
                }
                
                print("📱 AnalyticsView: Triggering scrapers")
                let result = try await NetworkService.shared.runScrapers()
                print("📱 AnalyticsView: Scrapers started successfully")
                
                // Load actual status after triggering scrapers
                await loadScraperStatus()
                
                // Start polling for status updates
                await pollScraperStatus()
                
            } catch {
                print("❌ AnalyticsView: Error running scrapers: \(error)")
                self.error = error
                
                withAnimation {
                    isRunningScrapers = false
                }
            }
        }
    }
    
    private func pollScraperStatus() async {
        print("📱 AnalyticsView: Starting status polling")
        repeat {
            do {
                await loadScraperStatus()
                try await Task.sleep(nanoseconds: 2_000_000_000) // 2 seconds between polls
            } catch {
                print("❌ AnalyticsView: Error polling status: \(error)")
                break
            }
            
            // Check if we should stop polling
            if let status = scraperStatus?.main_run.status,
               status != "running" {
                print("📱 AnalyticsView: Scraping completed with status: \(status)")
                
                // Reload properties one final time
                await loadProperties()
                
                withAnimation {
                    isRunningScrapers = false
                }
                break
            }
        } while isRunningScrapers
    }
}

struct StatItem: Identifiable {
    let id = UUID()
    let title: String
    let value: String
    let icon: String
    let valueSize: StatValueSize
    let showLoadingIndicator: Bool
    
    init(title: String, value: String, icon: String, valueSize: StatValueSize, showLoadingIndicator: Bool = false) {
        self.title = title
        self.value = value
        self.icon = icon
        self.valueSize = valueSize
        self.showLoadingIndicator = showLoadingIndicator
    }
}

enum StatValueSize {
    case medium
    case large
}

struct StatisticCard: View {
    let title: String
    let items: [StatItem]
    @State private var isHovered = false
    @State private var isAppeared = false
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            // Title with animated accent
            HStack {
                Text(title)
                    .font(.title3)
                    .fontWeight(.semibold)
                    .foregroundColor(.white)
                    .contentTransition(.interpolate)
                    .transition(.moveAndFade)
                
                Spacer()
                
                // Animated accent element
                Circle()
                    .fill(Theme.Colors.primary)
                    .frame(width: 8, height: 8)
                    .opacity(isHovered ? 1 : 0.6)
                    .scaleEffect(isHovered ? 1.2 : 1)
                    .blur(radius: isHovered ? 0.5 : 0)
                    .animation(.easeInOut(duration: 1).repeatForever(autoreverses: true), value: isHovered)
            }
            .padding(.horizontal, 16)
            .padding(.top, 16)
            
            VStack(spacing: 16) {
                ForEach(Array(items.enumerated()), id: \.element.id) { index, item in
                    StatItemView(item: item)
                        .transition(.asymmetric(
                            insertion: .move(edge: .trailing).combined(with: .opacity),
                            removal: .move(edge: .leading).combined(with: .opacity)
                        ))
                        .animation(.spring(response: 0.4, dampingFraction: 0.8).delay(Double(index) * 0.1), value: isAppeared)
                    
                    if item.id != items.last?.id {
                        Divider()
                            .background(Theme.Colors.secondary.opacity(0.2))
                    }
                }
            }
            .padding(.bottom, 16)
        }
        .background(
            ZStack {
                Theme.Colors.surface
                
                // Animated gradient overlay
                LinearGradient(
                    gradient: Gradient(colors: [
                        Theme.Colors.primary.opacity(isHovered ? 0.08 : 0.05),
                        Theme.Colors.primary.opacity(isHovered ? 0.04 : 0.02),
                        Color.clear
                    ]),
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )
                .animation(.easeInOut(duration: 0.5), value: isHovered)
            }
        )
        .cornerRadius(16)
        .shadow(
            color: Theme.Colors.primary.opacity(isHovered ? 0.15 : 0.1),
            radius: isHovered ? 15 : 10,
            x: 0,
            y: isHovered ? 8 : 5
        )
        .overlay(
            RoundedRectangle(cornerRadius: 16)
                .stroke(
                    Theme.Colors.primary.opacity(isHovered ? 0.15 : 0.1),
                    lineWidth: isHovered ? 1.5 : 1
                )
        )
        .scaleEffect(isHovered ? 1.02 : 1)
        .animation(.spring(response: 0.3, dampingFraction: 0.7), value: isHovered)
        .onHover { hovering in
            withAnimation(.easeInOut(duration: 0.2)) {
                isHovered = hovering
            }
        }
        .onAppear {
            withAnimation(.easeOut(duration: 0.5)) {
                isAppeared = true
            }
        }
    }
}

struct StatItemView: View {
    let item: StatItem
    @State private var isAppeared = false
    @State private var isHovered = false
    
    var body: some View {
        HStack(spacing: 16) {
            // Animated icon with background
            ZStack {
                Circle()
                    .fill(Theme.Colors.primary.opacity(isHovered ? 0.15 : 0.1))
                    .frame(width: 36, height: 36)
                    .scaleEffect(isHovered ? 1.1 : 1)
                
                Image(systemName: item.icon)
                    .font(.system(size: 16, weight: .medium))
                    .foregroundColor(Theme.Colors.primary)
                    .rotationEffect(.degrees(item.showLoadingIndicator ? 360 : 0))
                    .scaleEffect(isHovered ? 1.1 : 1)
                    .animation(
                        item.showLoadingIndicator ? 
                            .linear(duration: 2).repeatForever(autoreverses: false) : 
                            .spring(response: 0.3, dampingFraction: 0.7),
                        value: item.showLoadingIndicator || isHovered
                    )
            }
            
            VStack(alignment: .leading, spacing: 4) {
                Text(item.title)
                    .font(.subheadline)
                    .foregroundColor(Theme.Colors.secondary)
                    .contentTransition(.interpolate)
                
                HStack(spacing: 8) {
                    Text(item.value)
                        .font(item.valueSize == .large ? .title2 : .title3)
                        .fontWeight(.semibold)
                        .foregroundColor(.white)
                        .contentTransition(.numericText())
                    
                    if item.showLoadingIndicator {
                        LoadingDots()
                            .transition(.opacity)
                    }
                }
            }
            
            Spacer()
        }
        .padding(.horizontal, 16)
        .contentShape(Rectangle())
        .hoverEffect(.highlight)
        .opacity(isAppeared ? 1 : 0)
        .offset(y: isAppeared ? 0 : 10)
        .scaleEffect(isHovered ? 1.02 : 1, anchor: .leading)
        .animation(.spring(response: 0.3, dampingFraction: 0.8), value: isAppeared)
        .animation(.spring(response: 0.2, dampingFraction: 0.7), value: isHovered)
        .onHover { hovering in
            withAnimation {
                isHovered = hovering
            }
        }
        .onAppear {
            withAnimation(.easeOut(duration: 0.3).delay(0.1)) {
                isAppeared = true
            }
        }
    }
}

struct LoadingDots: View {
    @State private var isAnimating = false
    
    var body: some View {
        HStack(spacing: 4) {
            ForEach(0..<3) { index in
                Circle()
                    .fill(Theme.Colors.primary)
                    .frame(width: 4, height: 4)
                    .scaleEffect(isAnimating ? 1.2 : 0.5)
                    .opacity(isAnimating ? 1 : 0.3)
                    .blur(radius: isAnimating ? 0.5 : 0)
                    .animation(
                        .easeInOut(duration: 0.6)
                        .repeatForever()
                        .delay(0.2 * Double(index)),
                        value: isAnimating
                    )
            }
        }
        .onAppear {
            isAnimating = true
        }
    }
}

extension AnyTransition {
    static var moveAndFade: AnyTransition {
        .asymmetric(
            insertion: .move(edge: .trailing).combined(with: .opacity),
            removal: .scale.combined(with: .opacity)
        )
    }
}

extension View {
    func pressAnimation() -> some View {
        self.modifier(PressAnimationModifier())
    }
}

struct PressAnimationModifier: ViewModifier {
    @State private var isPressed = false
    
    func body(content: Content) -> some View {
        content
            .scaleEffect(isPressed ? 0.98 : 1)
            .animation(.spring(response: 0.3, dampingFraction: 0.7), value: isPressed)
            .onTapGesture {
                withAnimation(.easeInOut(duration: 0.1)) {
                    isPressed = true
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
                        isPressed = false
                    }
                }
            }
    }
}

struct ScraperButtonStyle: ButtonStyle {
    @State private var isPressed = false
    
    func makeBody(configuration: Configuration) -> some View {
        configuration.label
            .scaleEffect(configuration.isPressed ? 0.95 : 1.0)
            .opacity(configuration.isPressed ? 0.9 : 1.0)
            .animation(.spring(response: 0.2, dampingFraction: 0.7), value: configuration.isPressed)
            .onChange(of: configuration.isPressed) { pressed in
                isPressed = pressed
            }
    }
}

#Preview {
    AnalyticsView()
        .preferredColorScheme(.dark)
} 