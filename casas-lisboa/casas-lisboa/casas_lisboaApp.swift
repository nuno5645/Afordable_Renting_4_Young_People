//
//  casas_lisboaApp.swift
//  casas-lisboa
//
//  Created by Nuno Ferreira on 07/03/2025.
//

import SwiftUI

@main
struct casas_lisboaApp: App {
    @StateObject private var authService = AuthenticationService()
    @StateObject private var notificationService = NotificationService.shared
    
    init() {
        // Request notification permissions when app launches
        UNUserNotificationCenter.current().delegate = NotificationDelegate.shared
    }
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(authService)
                .onAppear {
                    notificationService.scheduleHelloWorldNotification()
                }
        }
    }
}

// Notification delegate to handle foreground notifications
class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {
    static let shared = NotificationDelegate()
    
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        // Show notification even when app is in foreground
        completionHandler([.banner, .sound])
    }
}
