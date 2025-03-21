import Foundation

struct User: Codable, Identifiable {
    var id: Int {
        // Since the API doesn't return an ID in the profile endpoint, we'll use a computed property
        // This is temporary until we update the API to include the ID
        return 0
    }
    let email: String
    let username: String
    var profile: UserProfile?
    
    enum CodingKeys: String, CodingKey {
        case email, username, profile
    }
}

struct UserProfile: Codable {
    var profilePicture: String?
    var phoneNumber: String?
    var preferredZones: [String]
    var priceRangeMin: Double?
    var priceRangeMax: Double?
    var minBedrooms: Int?
    var minArea: Int?
    var notificationEnabled: Bool
    
    enum CodingKeys: String, CodingKey {
        case profilePicture = "profile_picture"
        case phoneNumber = "phone_number"
        case preferredZones = "preferred_zones"
        case priceRangeMin = "price_range_min"
        case priceRangeMax = "price_range_max"
        case minBedrooms = "min_bedrooms"
        case minArea = "min_area"
        case notificationEnabled = "notification_enabled"
    }
    
    init(phoneNumber: String? = nil,
         preferredZones: [String] = [],
         priceRangeMin: Double? = nil,
         priceRangeMax: Double? = nil,
         minBedrooms: Int? = nil,
         minArea: Int? = nil,
         notificationEnabled: Bool = true,
         profilePicture: String? = nil) {
        self.phoneNumber = phoneNumber
        self.preferredZones = preferredZones
        self.priceRangeMin = priceRangeMin
        self.priceRangeMax = priceRangeMax
        self.minBedrooms = minBedrooms
        self.minArea = minArea
        self.notificationEnabled = notificationEnabled
        self.profilePicture = profilePicture
    }
    
    // Add custom decoding for handling string-based decimal values
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        profilePicture = try container.decodeIfPresent(String.self, forKey: .profilePicture)
        phoneNumber = try container.decodeIfPresent(String.self, forKey: .phoneNumber)
        preferredZones = try container.decode([String].self, forKey: .preferredZones)
        notificationEnabled = try container.decode(Bool.self, forKey: .notificationEnabled)
        minBedrooms = try container.decodeIfPresent(Int.self, forKey: .minBedrooms)
        minArea = try container.decodeIfPresent(Int.self, forKey: .minArea)
        
        // Handle price range values that might come as strings
        if let minString = try container.decodeIfPresent(String.self, forKey: .priceRangeMin) {
            priceRangeMin = Double(minString)
        } else {
            priceRangeMin = try container.decodeIfPresent(Double.self, forKey: .priceRangeMin)
        }
        
        if let maxString = try container.decodeIfPresent(String.self, forKey: .priceRangeMax) {
            priceRangeMax = Double(maxString)
        } else {
            priceRangeMax = try container.decodeIfPresent(Double.self, forKey: .priceRangeMax)
        }
    }
}

// Authentication related models
struct LoginCredentials: Codable {
    let email: String
    let password: String
}

struct RegisterCredentials: Codable {
    let email: String
    let username: String
    let password: String
    let password2: String
    var profile: UserProfile?
    
    enum CodingKeys: String, CodingKey {
        case email, username, password, password2, profile
    }
}

struct AuthResponse: Codable {
    let access: String
    let refresh: String
}

struct TokenRefreshRequest: Codable {
    let refresh: String
}

struct PasswordChangeRequest: Codable {
    let oldPassword: String
    let newPassword: String
    let newPassword2: String
    
    enum CodingKeys: String, CodingKey {
        case oldPassword = "old_password"
        case newPassword = "new_password"
        case newPassword2 = "new_password2"
    }
}

struct PasswordResetRequest: Codable {
    let email: String
}

struct PasswordResetConfirmRequest: Codable {
    let token: String
    let newPassword: String
    let newPassword2: String
    
    enum CodingKeys: String, CodingKey {
        case token
        case newPassword = "new_password"
        case newPassword2 = "new_password2"
    }
} 