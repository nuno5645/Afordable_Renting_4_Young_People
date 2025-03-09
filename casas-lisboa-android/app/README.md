# Lisbon Rentals Android App

A modern Android application built with Jetpack Compose for browsing rental properties in Lisbon, Portugal.

## Features

- Browse rental listings with detailed information
- View property images with navigation controls
- Mark properties as favorites
- Contact property owners via email
- Schedule property visits
- Filter properties based on preferences
- Bottom navigation for easy access to different sections

## Screenshots

![App Screenshot](screenshot.png)

## Architecture

The app follows a clean architecture approach with the following components:

- **UI Layer**: Jetpack Compose UI components
  - Screens: Home, Favorites, Search, Analytics, Profile
  - Components: PropertyCard, TopAppBar, BottomNavigation
- **Domain Layer**: Business logic and models
  - Models: RentalProperty
- **Data Layer**: (To be implemented) Repository pattern for data access

## Tech Stack

- **Kotlin**: Primary programming language
- **Jetpack Compose**: Modern UI toolkit for building native UI
- **Material Design 3**: Design system for consistent and beautiful UI
- **Coil**: Image loading library for efficient image loading
- **Android Architecture Components**: For robust and maintainable architecture

## Project Structure

```
src/main/java/com.casaslisboa/
├── model/
│   └── RentalProperty.kt
├── ui/
│   ├── components/
│   │   ├── BottomNavigation.kt
│   │   ├── PropertyCard.kt
│   │   └── TopAppBar.kt
│   ├── screens/
│   │   └── HomeScreen.kt
│   └── theme/
│       ├── Color.kt
│       ├── Theme.kt
│       └── Type.kt
└── MainActivity.kt
```

## Getting Started

1. Clone the repository
2. Open the project in Android Studio
3. Build and run the app on an emulator or physical device

## Future Enhancements

- Implement real data fetching from a backend API
- Add property details screen
- Implement search functionality
- Add filtering options
- Implement user authentication
- Add map view for property locations

## License

This project is licensed under the MIT License - see the LICENSE file for details. 