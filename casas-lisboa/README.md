# Casas Lisboa

A SwiftUI app for browsing and tracking rental properties in Lisbon. The app provides a modern, user-friendly interface for searching and filtering rental listings.

## Features

### Implemented
- Browse rental properties with detailed information including:
  - Price
  - Location
  - Area
  - Number of bedrooms
  - Property source
- Advanced filtering system with:
  - Price range selection
  - Area range filtering
  - Bedroom count filtering
  - Source filtering
- Modern card-based property listing interface
- Responsive and adaptive UI design
- Dark mode support
- Smooth animations and transitions

### In Development
- Property details screen with comprehensive information
- Favorites system for saving interesting properties
- Integration with backend API
- Search functionality
- User preferences persistence

## Technical Details

### Architecture
- SwiftUI-based UI implementation
- MVVM architecture pattern
- Modular view components for reusability
- Responsive layout adapting to different screen sizes

### Key Components
- `HomeView`: Main listing interface with property cards
- `FilterView`: Advanced filtering interface with multiple criteria
- `PropertyCardView`: Reusable card component for property listings

## Requirements

- iOS 15.0+
- Xcode 14.0+
- Swift 5.7+

## Installation

1. Clone the repository
2. Open `casas-lisboa.xcodeproj` in Xcode
3. Build and run the app on your device or simulator

## Project Structure

```
casas-lisboa/
├── Views/
│   ├── HomeView.swift         # Main listing view
│   ├── FilterView.swift       # Property filtering interface
│   └── PropertyCardView.swift # Property card component
├── Models/                    # Data models
└── Assets/                    # App resources
```

## Future Enhancements

### Short Term
- Implement property details view
- Add favorites functionality
- Connect to the web scraping backend API
- Add search functionality
- Implement data persistence

### Long Term
- User authentication and profiles
- Property alerts and notifications
- Analytics dashboard
- Map view for property locations
- Sharing functionality
- Comparison tools

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is proprietary and confidential. 