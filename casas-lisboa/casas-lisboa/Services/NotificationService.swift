import Foundation
import UserNotifications

class NotificationService: ObservableObject {
    static let shared = NotificationService()
    
    init() {
        requestAuthorization()
    }
    
    func requestAuthorization() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .badge, .sound]) { success, error in
            if success {
                print("Notification authorization granted")
            } else if let error = error {
                print("Error requesting notification authorization: \(error.localizedDescription)")
            }
        }
    }
    
    func scheduleHelloWorldNotification() {
        let content = UNMutableNotificationContent()
        content.title = "Hello!"
        content.body = "Welcome to Casas Lisboa"
        content.sound = .default
        
        // Trigger notification in 5 seconds
        let trigger = UNTimeIntervalNotificationTrigger(timeInterval: 5, repeats: false)
        
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: trigger
        )
        
        UNUserNotificationCenter.current().add(request) { error in
            if let error = error {
                print("Error scheduling notification: \(error.localizedDescription)")
            } else {
                print("Hello World notification scheduled successfully")
            }
        }
    }
} 