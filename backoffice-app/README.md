# Casas Lisboa - Backoffice

A modern Next.js backoffice application for managing affordable rental properties in the Lisbon area.

## Features

✨ **Dashboard** - Overview of your rental properties with statistics  
🏠 **House Management** - Browse, filter, and manage properties  
⭐ **Favorites** - Mark properties as favorites  
💬 **Contact Tracking** - Track which properties you've contacted  
🗑️ **Discard Feature** - Mark unwanted properties  
🤖 **Scraper Management** - Monitor and trigger data scrapers  
🔐 **Authentication** - Secure JWT-based authentication  
📱 **Responsive Design** - Works on desktop and mobile devices

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Notifications**: React Hot Toast
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Django API running on `http://localhost:8000` (see `../django_api/`)

### Installation

1. Install dependencies:
```bash
npm install
```

2. The `.env.local` file is already configured with:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Development

Run the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

You'll be redirected to the login page. Register a new account or login with existing credentials.

### Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
backoffice-app/
├── app/                    # Next.js app directory
│   ├── dashboard/         # Dashboard pages
│   │   ├── houses/       # House management
│   │   ├── scrapers/     # Scraper monitoring
│   │   └── settings/     # User settings
│   ├── login/            # Login page
│   ├── register/         # Registration page
│   └── layout.tsx        # Root layout
├── components/            # React components
│   ├── ui/               # UI components (Button, Card, Input)
│   └── Navbar.tsx        # Navigation component
├── lib/                   # Utilities and API client
│   ├── api.ts            # API client and types
│   └── utils.ts          # Helper functions
└── public/               # Static assets
```

## API Integration

The backoffice connects to the Django REST API with the following endpoints:

### Authentication
- `POST /api/users/login/` - User login
- `POST /api/users/register/` - User registration
- `POST /api/users/logout/` - User logout
- `GET /api/users/profile/` - Get user profile

### Houses
- `GET /api/houses/` - List all houses
- `GET /api/houses/{id}/` - Get house details
- `POST /api/houses/{id}/toggle_favorite/` - Toggle favorite status
- `POST /api/houses/{id}/toggle_contacted/` - Toggle contacted status
- `POST /api/houses/{id}/toggle_discarded/` - Toggle discarded status
- `DELETE /api/houses/{id}/` - Delete house

### Scrapers
- `GET /api/scraper-status/` - Get scraper status
- `POST /api/run-scrapers/` - Trigger scrapers

## Features in Detail

### Dashboard
- Statistics overview (total houses, favorites, contacted, average price)
- Recent properties list
- Scraper status summary

### House Management
- Search and filter properties
- Filter by source, favorites, contacted, or discarded
- View property details with images
- Quick actions (favorite, contact, discard)
- External link to original listing

### Scraper Management
- View status of all scrapers
- See last run time and houses found
- Manually trigger scraper runs
- View error messages

### Settings
- View profile information
- See search preferences
- API access information

## Troubleshooting

### Cannot connect to API
- Ensure the Django API is running on `http://localhost:8000`
- Check CORS settings in the Django API
- Verify network connectivity

### Authentication issues
- Clear localStorage and try logging in again
- Check if JWT tokens are properly configured in the Django API

### Build errors
- Run `npm install` to ensure all dependencies are installed
- Clear Next.js cache: `rm -rf .next`
- Check Node.js version (requires 18+)

## License

This project is part of the Casas Lisboa platform for finding affordable rental properties.
