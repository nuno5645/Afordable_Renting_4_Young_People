import Foundation
#if targetEnvironment(simulator)
    private let baseURL = "https://localhost:8080/api"
#else
    private let baseURL = "https://100.95.208.157:8080/api"
#endif

struct APIResponse: Codable {
    let count: Int
    let next: String?
    let previous: String?
    let results: [HouseResponse]
}

struct HouseResponse: Codable {
    let name: String
    let zone: String
    let price: String
    let url: String
    let bedrooms: String
    let area: String
    let source: String
    let imageUrls: String?
    let contacted: Bool
    let favorite: Bool
    let discarded: Bool
    let houseId: String
    let scrapedAt: String
    
    enum CodingKeys: String, CodingKey {
        case name, zone, price, url, bedrooms, area, source
        case imageUrls = "image_urls"
        case contacted, favorite, discarded
        case houseId = "house_id"
        case scrapedAt = "scraped_at"
    }
}

class NetworkService: NSObject, URLSessionDelegate {
    static let shared = NetworkService()
    
    // Create a custom URLSession with this class as the delegate and make it internal instead of private
    lazy var session: URLSession = {
        let configuration = URLSessionConfiguration.default
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
    
    func fetchHouses() async throws -> [Property] {
        print("🌐 NetworkService: Starting fetchHouses request")
        let url = URL(string: "\(baseURL)/houses/")!
        print("🌐 NetworkService: Request URL: \(url.absoluteString)")
        
        do {
            print("🌐 NetworkService: Initiating URL request")
            // Use custom session with certificate trust handling instead of shared session
            let (data, response) = try await session.data(from: url)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🌐 NetworkService: Received response with status code: \(httpResponse.statusCode)")
                print("🌐 NetworkService: Response headers: \(httpResponse.allHeaderFields)")
            }
            
            print("🌐 NetworkService: Received data of size: \(data.count) bytes")
            if let dataString = String(data: data.prefix(200), encoding: .utf8) {
                print("🌐 NetworkService: First 200 characters of response: \(dataString)...")
            }
            
            let decoder = JSONDecoder()
            do {
                print("🌐 NetworkService: Attempting to decode response")
                let response = try decoder.decode(APIResponse.self, from: data)
                print("🌐 NetworkService: Successfully decoded response with \(response.results.count) houses")
                
                let dateFormatter = ISO8601DateFormatter()
                dateFormatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
                
                let properties = response.results
                    .compactMap { house -> Property? in
                        guard let date = dateFormatter.date(from: house.scrapedAt) else {
                            print("⚠️ NetworkService: Failed to parse date for house: \(house.houseId)")
                            return nil
                        }
                        
                        let imageUrlArray = house.imageUrls?.components(separatedBy: "|||") ?? []
                        
                        return Property(
                            id: UUID(uuidString: house.houseId) ?? UUID(),
                            houseId: house.houseId,
                            price: Int(Double(house.price) ?? 0),
                            location: house.zone,
                            bedrooms: Int(house.bedrooms) ?? 0,
                            area: Double(house.area) ?? 0,
                            source: house.source,
                            hasPhoto: !imageUrlArray.isEmpty,
                            isFavorite: house.favorite,
                            contacted: house.contacted,
                            discarded: house.discarded,
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
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        
        do {
            let (_, response) = try await session.data(for: request)
            
            if let httpResponse = response as? HTTPURLResponse {
                print("🌐 NetworkService: Received response with status code: \(httpResponse.statusCode)")
                
                guard (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }
            }
        } catch {
            print("❌ NetworkService: Failed to toggle discarded status: \(error.localizedDescription)")
            throw error
        }
    }
} 