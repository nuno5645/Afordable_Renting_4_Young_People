import Foundation
import KeychainSwift
#if targetEnvironment(simulator)
    private let baseURL = "https://localhost:8080/api"
#else
    private let baseURL = "https://100.95.208.157:8080/api"
#endif

// This struct is for when the API returns a wrapped response with a 'results' field
// Currently not used as the API returns an array directly
struct APIResponse: Codable {
    let results: [HouseResponse]
}

struct HouseResponse: Codable {
    let name: String
    let zone: String
    let price: String
    let url: String
    let bedrooms: String
    let area: String
    let area_str: String?
    let source: String
    let imageUrls: String?
    let is_contacted: Bool
    let is_favorite: Bool
    let is_discarded: Bool
    let houseId: String
    let scrapedAt: String
    
    enum CodingKeys: String, CodingKey {
        case name, zone, price, url, bedrooms, area, area_str, source
        case imageUrls = "image_urls"
        case is_contacted, is_favorite, is_discarded
        case houseId = "house_id"
        case scrapedAt = "scraped_at"
    }
}

// Update the ScraperStatusResponse struct to match the new API response format
struct MainRunStatus: Codable {
    let status: String
    let start_time: String?
    let end_time: String?
    let total_houses: Int
    let new_houses: Int
    let error_message: String?
    let last_run_date: String?
}

struct ScraperStatusResponse: Codable {
    let name: String
    let status: String
    let timestamp: String
    let houses_processed: Int
    let houses_found: Int
    let error_message: String?
}

struct ScraperStatusData: Codable {
    let main_run: MainRunStatus
    let scrapers: [String: ScraperStatusResponse]
}

class NetworkService: NSObject, URLSessionDelegate {
    static let shared = NetworkService()
    
    // Create a custom URLSession with this class as the delegate and make it internal instead of private
    lazy var session: URLSession = {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30  // 30 seconds timeout for regular requests
        return URLSession(configuration: configuration, delegate: self, delegateQueue: nil)
    }()
    
    // Create a separate session with longer timeout for scraper operations
    lazy var scraperSession: URLSession = {
        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 1200  // 20 minutes timeout for scraper requests
        return URLSession(configuration: configuration, delegate: self, delegateQueue: nil)
    }()
    
    // URLSession delegate method to handle SSL certificate trust
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge, completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        print("🔒 NetworkService: Handling SSL challenge for host: \(challenge.protectionSpace.host)")
        
        // Trust certificates for both our server and localhost
        if challenge.protectionSpace.host == "100.95.208.157" || challenge.protectionSpace.host == "localhost" {
            print("🔒 NetworkService: Accepting certificate for host: \(challenge.protectionSpace.host)")
            let credential = URLCredential(trust: challenge.protectionSpace.serverTrust!)
            completionHandler(.useCredential, credential)
        } else {
            // Use default handling for other domains
            print("🔒 NetworkService: Using default handling for host: \(challenge.protectionSpace.host)")
            completionHandler(.performDefaultHandling, nil)
        }
    }
    
    // Helper method to create authenticated requests
    private func createAuthenticatedRequest(url: URL) -> URLRequest {
        var request = URLRequest(url: url)
        if let accessToken = KeychainSwift().get("accessToken") {
            request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
        }
        return request
    }
    
    func fetchHouses() async throws -> [Property] {
        print("🌐 NetworkService: Starting fetchHouses request")
        let url = URL(string: "\(baseURL)/houses/")!
        print("🌐 NetworkService: Request URL: \(url.absoluteString)")
        
        let request = createAuthenticatedRequest(url: url)
        
        do {
            print("🌐 NetworkService: Initiating URL request")
            let (data, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🌐 NetworkService: Received response with status code: \(httpResponse.statusCode)")
                print("🌐 NetworkService: Response headers: \(httpResponse.allHeaderFields)")
                
                // Handle authentication errors
                if httpResponse.statusCode == 401 {
                    print("🌐 NetworkService: Authentication required")
                    throw URLError(.userAuthenticationRequired)
                }
            }
            
            print("🌐 NetworkService: Received data of size: \(data.count) bytes")
            if let dataString = String(data: data.prefix(200), encoding: .utf8) {
                print("🌐 NetworkService: First 200 characters of response: \(dataString)...")
            }
            
            let decoder = JSONDecoder()
            do {
                print("🌐 NetworkService: Attempting to decode response")
                
                // Try to decode as array directly since the API is returning an array
                let houses = try decoder.decode([HouseResponse].self, from: data)
                print("🌐 NetworkService: Successfully decoded response with \(houses.count) houses")
                
                let dateFormatter = ISO8601DateFormatter()
                dateFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
                
                let properties = houses
                    .compactMap { house -> Property? in
                        guard let date = dateFormatter.date(from: house.scrapedAt) else {
                            print("⚠️ NetworkService: Failed to parse date for house: \(house.houseId)")
                            return nil
                        }
                        
                        let imageUrlArray = house.imageUrls?.components(separatedBy: "|||") ?? []
                        
                        // Log area values for debugging
                        if house.area_str == nil {
                            print("⚠️ NetworkService: House \(house.houseId) has null area_str, using numeric area: \(house.area)")
                        }
                        
                        return Property(
                            id: UUID(uuidString: house.houseId) ?? UUID(),
                            houseId: house.houseId,
                            price: Int(Double(house.price) ?? 0),
                            location: house.zone,
                            bedrooms: Int(house.bedrooms) ?? 0,
                            area: Double(house.area) ?? 0,
                            areaStr: house.area_str ?? "",
                            source: house.source,
                            hasPhoto: !imageUrlArray.isEmpty,
                            isFavorite: house.is_favorite,
                            contacted: house.is_contacted,
                            discarded: house.is_discarded,
                            name: house.name,
                            imageUrls: imageUrlArray,
                            url: house.url,
                            scrapedAt: date
                        )
                    }
                
                print("🌐 NetworkService: Successfully mapped \(properties.count) properties")
                return properties.sorted { $0.scrapedAt > $1.scrapedAt }
                
            } catch {
                print("❌ NetworkService: JSON Decoding Error: \(error)")
                print("❌ NetworkService: Error Description: \(error.localizedDescription)")
                if let decodingError = error as? DecodingError {
                    switch decodingError {
                    case .dataCorrupted(let context):
                        print("❌ NetworkService: Data Corrupted: \(context.debugDescription)")
                    case .keyNotFound(let key, let context):
                        print("❌ NetworkService: Key '\(key)' not found: \(context.debugDescription)")
                    case .typeMismatch(let type, let context):
                        print("❌ NetworkService: Type '\(type)' mismatch: \(context.debugDescription)")
                    case .valueNotFound(let type, let context):
                        print("❌ NetworkService: Value of type '\(type)' not found: \(context.debugDescription)")
                    @unknown default:
                        print("❌ NetworkService: Unknown decoding error")
                    }
                }
                throw error
            }
            
        } catch {
            print("❌ NetworkService: Network Error: \(error)")
            print("❌ NetworkService: Error Description: \(error.localizedDescription)")
            if let urlError = error as? URLError {
                print("❌ NetworkService: URL Error Code: \(urlError.code.rawValue)")
                print("❌ NetworkService: URL Error Description: \(urlError.localizedDescription)")
            }
            throw error
        }
    }
    
    func toggleDiscarded(for houseId: String) async throws {
        print("🌐 NetworkService: Toggling discarded status for house \(houseId)")
        let url = URL(string: "\(baseURL)/houses/\(houseId)/toggle_discarded/")!
        
        var request = createAuthenticatedRequest(url: url)
        request.httpMethod = "POST"
        
        do {
            let (_, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🌐 NetworkService: Received response with status code: \(httpResponse.statusCode)")
                
                if httpResponse.statusCode == 401 {
                    print("🌐 NetworkService: Authentication required")
                    throw URLError(.userAuthenticationRequired)
                }
                
                guard (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }
            }
        } catch {
            print("❌ NetworkService: Failed to toggle discarded status: \(error.localizedDescription)")
            throw error
        }
    }
    
    func toggleFavorite(for houseId: String) async throws {
        print("🌐 NetworkService: Toggling favorite status for house \(houseId)")
        let url = URL(string: "\(baseURL)/houses/\(houseId)/toggle_favorite/")!
        
        var request = createAuthenticatedRequest(url: url)
        request.httpMethod = "POST"
        
        do {
            let (_, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🌐 NetworkService: Received response with status code: \(httpResponse.statusCode)")
                
                if httpResponse.statusCode == 401 {
                    print("🌐 NetworkService: Authentication required")
                    throw URLError(.userAuthenticationRequired)
                }
                
                guard (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }
            }
        } catch {
            print("❌ NetworkService: Failed to toggle favorite status: \(error.localizedDescription)")
            throw error
        }
    }
    
    func toggleContacted(for houseId: String) async throws {
        print("🌐 NetworkService: Toggling contacted status for house \(houseId)")
        let url = URL(string: "\(baseURL)/houses/\(houseId)/toggle_contacted/")!
        
        var request = createAuthenticatedRequest(url: url)
        request.httpMethod = "POST"
        
        do {
            let (_, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🌐 NetworkService: Received response with status code: \(httpResponse.statusCode)")
                
                if httpResponse.statusCode == 401 {
                    print("🌐 NetworkService: Authentication required")
                    throw URLError(.userAuthenticationRequired)
                }
                
                guard (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }
            }
        } catch {
            print("❌ NetworkService: Failed to toggle contacted status: \(error.localizedDescription)")
            throw error
        }
    }
    
    func runScrapers() async throws -> [String: (total: Int, new: Int)] {
        print("🌐 NetworkService: Triggering run-scrapers endpoint")
        let url = URL(string: "\(baseURL)/run-scrapers/")!
        print("🌐 NetworkService: Request URL: \(url.absoluteString)")
        
        var request = createAuthenticatedRequest(url: url)
        request.httpMethod = "POST"
        
        do {
            print("🌐 NetworkService: Sending POST request to run scrapers")
            let (data, response) = try await scraperSession.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🌐 NetworkService: Received response with status code: \(httpResponse.statusCode)")
                print("🌐 NetworkService: Response headers: \(httpResponse.allHeaderFields)")
                
                if httpResponse.statusCode == 401 {
                    print("❌ NetworkService: Authentication required")
                    throw URLError(.userAuthenticationRequired)
                }
                
                guard (200...299).contains(httpResponse.statusCode) else {
                    print("❌ NetworkService: Bad response status code")
                    throw URLError(.badServerResponse)
                }
            }
            
            // Debug print the raw response data
            print("🌐 NetworkService: Raw response data size: \(data.count) bytes")
            if let jsonString = String(data: data, encoding: .utf8) {
                print("🌐 NetworkService: Raw JSON response:")
                print(jsonString)
            }
            
            // Decode the response
            let decoder = JSONDecoder()
            
            // First try to decode as RunScrapersResponse
            struct RunScrapersResponse: Codable {
                let status: String
                let output: String
            }
            
            do {
                let runResponse = try decoder.decode(RunScrapersResponse.self, from: data)
                print("🌐 NetworkService: Successfully started scrapers. Status: \(runResponse.status)")
                
                // Since the scrapers are now running, we'll return an empty result
                // The actual results will be available through the scraper status endpoint
                return [:]
            } catch {
                print("❌ NetworkService: Failed to decode run scrapers response: \(error)")
                throw error
            }
        } catch {
            print("❌ NetworkService: Failed to run scrapers: \(error.localizedDescription)")
            throw error
        }
    }
    
    func getScraperStatus() async throws -> [String: ScraperStatusResponse] {
        print("🔍 NetworkService: Fetching individual scraper status from /scraper-status/")
        let url = URL(string: "\(baseURL)/scraper-status/")!
        print("🔍 NetworkService: Request URL: \(url.absoluteString)")
        
        let request = createAuthenticatedRequest(url: url)
        
        do {
            let (data, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🔍 NetworkService: Received response with status code: \(httpResponse.statusCode)")
                print("🔍 NetworkService: Response headers: \(httpResponse.allHeaderFields)")
                
                if httpResponse.statusCode == 401 {
                    print("🔍 NetworkService: Authentication required")
                    throw URLError(.userAuthenticationRequired)
                }
                
                guard (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }
            }
            
            // Debug print the raw response data
            print("🔍 NetworkService: Raw response data size: \(data.count) bytes")
            if let jsonString = String(data: data, encoding: .utf8) {
                print("🔍 NetworkService: Raw JSON response for individual scrapers:")
                print(jsonString)
            }
            
            let decoder = JSONDecoder()
            let status = try decoder.decode([String: ScraperStatusResponse].self, from: data)
            print("🔍 NetworkService: Successfully decoded individual scraper statuses for \(status.count) scrapers")
            for (scraperName, scraperStatus) in status {
                print("🔍 Scraper '\(scraperName)': Status=\(scraperStatus.status), Houses Processed=\(scraperStatus.houses_processed), Houses Found=\(scraperStatus.houses_found)")
            }
            return status
        } catch {
            print("❌ NetworkService: Failed to fetch individual scraper status: \(error)")
            if let decodingError = error as? DecodingError {
                switch decodingError {
                case .dataCorrupted(let context):
                    print("❌ NetworkService: Data Corrupted: \(context.debugDescription)")
                case .keyNotFound(let key, let context):
                    print("❌ NetworkService: Key '\(key)' not found: \(context.debugDescription)")
                case .typeMismatch(let type, let context):
                    print("❌ NetworkService: Type '\(type)' mismatch: \(context.debugDescription)")
                case .valueNotFound(let type, let context):
                    print("❌ NetworkService: Value of type '\(type)' not found: \(context.debugDescription)")
                @unknown default:
                    print("❌ NetworkService: Unknown decoding error")
                }
            }
            throw error
        }
    }
    
    func fetchScraperStatus() async throws -> ScraperStatusData {
        print("📊 NetworkService: Fetching overall scraper status from /houses/scraper_status/")
        let url = URL(string: "\(baseURL)/houses/scraper_status/")!
        print("📊 NetworkService: Request URL: \(url.absoluteString)")
        
        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        
        // Add authentication token
        if let accessToken = KeychainSwift().get("accessToken") {
            request.setValue("Bearer \(accessToken)", forHTTPHeaderField: "Authorization")
            print("📊 NetworkService: Added authentication token to request")
        } else {
            print("❌ NetworkService: No access token found")
            throw URLError(.userAuthenticationRequired)
        }
        
        do {
            let (data, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("📊 NetworkService: Received response with status code: \(httpResponse.statusCode)")
                print("📊 NetworkService: Response headers: \(httpResponse.allHeaderFields)")
                
                if httpResponse.statusCode == 401 {
                    print("❌ NetworkService: Authentication failed")
                    throw URLError(.userAuthenticationRequired)
                }
            }
            
            // Debug print the raw response data
            print("📊 NetworkService: Raw response data size: \(data.count) bytes")
            if let jsonString = String(data: data, encoding: .utf8) {
                print("📊 NetworkService: Raw JSON response for overall status:")
                print(jsonString)
            }
            
            let decoder = JSONDecoder()
            do {
                let statusData = try decoder.decode(ScraperStatusData.self, from: data)
                print("📊 NetworkService: Successfully decoded overall scraper status")
                print("📊 Main run status: \(statusData.main_run.status)")
                print("📊 Total houses: \(statusData.main_run.total_houses), New houses: \(statusData.main_run.new_houses)")
                print("📊 Individual scrapers status:")
                for (scraperName, status) in statusData.scrapers {
                    print("📊 Scraper '\(scraperName)': Status=\(status.status), Houses Processed=\(status.houses_processed), Houses Found=\(status.houses_found)")
                }
                return statusData
            } catch {
                print("❌ NetworkService: JSON Decoding Error: \(error)")
                if let decodingError = error as? DecodingError {
                    switch decodingError {
                    case .dataCorrupted(let context):
                        print("❌ NetworkService: Data Corrupted: \(context.debugDescription)")
                    case .keyNotFound(let key, let context):
                        print("❌ NetworkService: Key '\(key)' not found: \(context.debugDescription)")
                    case .typeMismatch(let type, let context):
                        print("❌ NetworkService: Type '\(type)' mismatch: \(context.debugDescription)")
                    case .valueNotFound(let type, let context):
                        print("❌ NetworkService: Value of type '\(type)' not found: \(context.debugDescription)")
                    @unknown default:
                        print("❌ NetworkService: Unknown decoding error")
                    }
                }
                throw error
            }
        } catch {
            print("❌ NetworkService: Network error while fetching overall scraper status: \(error)")
            throw error
        }
    }
    
    func updateUserPreferences(minPrice: Double?, maxPrice: Double?, minBedrooms: Int?, minArea: Int?, notificationEnabled: Bool) async throws -> User {
        print("🌐 NetworkService: Updating user preferences")
        let url = URL(string: "\(baseURL)/users/profile/")!
        print("🌐 NetworkService: Request URL: \(url.absoluteString)")
        
        var request = createAuthenticatedRequest(url: url)
        request.httpMethod = "PATCH"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        
        let preferences = [
            "price_range_min": minPrice,
            "price_range_max": maxPrice,
            "min_bedrooms": minBedrooms,
            "min_area": minArea,
            "notification_enabled": notificationEnabled
        ] as [String : Any?]
        
        // Filter out nil values
        let filteredPreferences = preferences.compactMapValues { $0 }
        
        let jsonData = try JSONSerialization.data(withJSONObject: filteredPreferences)
        request.httpBody = jsonData
        
        do {
            let (data, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🌐 NetworkService: Received response with status code: \(httpResponse.statusCode)")
                
                if httpResponse.statusCode == 401 {
                    print("🌐 NetworkService: Authentication required")
                    throw URLError(.userAuthenticationRequired)
                }
                
                guard (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }
            }
            
            // Debug print the response
            if let jsonString = String(data: data, encoding: .utf8) {
                print("🌐 NetworkService: Response data: \(jsonString)")
            }
            
            let decoder = JSONDecoder()
            let updatedUser = try decoder.decode(User.self, from: data)
            return updatedUser
        } catch {
            print("❌ NetworkService: Failed to update preferences: \(error.localizedDescription)")
            if let decodingError = error as? DecodingError {
                switch decodingError {
                case .dataCorrupted(let context):
                    print("❌ NetworkService: Data Corrupted: \(context.debugDescription)")
                case .keyNotFound(let key, let context):
                    print("❌ NetworkService: Key '\(key)' not found: \(context.debugDescription)")
                case .typeMismatch(let type, let context):
                    print("❌ NetworkService: Type '\(type)' mismatch: \(context.debugDescription)")
                case .valueNotFound(let type, let context):
                    print("❌ NetworkService: Value of type '\(type)' not found: \(context.debugDescription)")
                @unknown default:
                    print("❌ NetworkService: Unknown decoding error")
                }
            }
            throw error
        }
    }
} 
