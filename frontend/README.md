# myCv Frontend

Modern React application for CV generation and management.

## Tech Stack

- **React 18** with **TypeScript**
- **Vite** for fast development and building
- **Mantine UI** for beautiful, accessible components
- **React Router** for navigation
- **TanStack Query** for server state management
- **Axios** for API calls

## Features

- ✅ **Authentication** - JWT-based login/signup
- ✅ **Dashboard** - Manage multiple CVs with status tracking
- ✅ **CV Generation** - Create optimized CVs for specific job descriptions
- ✅ **Settings** - Configure AI provider, model, and API keys
- ✅ **Real-time Updates** - Auto-polling for CV generation status
- ⏳ **Profile Editor** - Edit personal data and CV content (coming soon)

## Project Structure

```
src/
├── components/        # Reusable components
│   ├── AppLayout.tsx
│   └── ProtectedRoute.tsx
├── contexts/          # React contexts
│   └── AuthContext.tsx
├── pages/             # Page components
│   ├── Login.tsx
│   ├── Signup.tsx
│   ├── Dashboard.tsx
│   ├── Profile.tsx
│   └── Settings.tsx
├── services/          # API client
│   └── api.ts
├── types/             # TypeScript types
│   └── index.ts
└── App.tsx            # Main app with routing
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on http://localhost:3000

### Installation

```bash
npm install
```

### Development

```bash
npm run dev
```

The app will be available at http://localhost:5173/

### Build

```bash
npm run build
```

### Preview Production Build

```bash
npm run preview
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:3000
```

## API Integration

The app connects to the FastAPI backend at `http://localhost:3000` by default.

All API calls are handled through `src/services/api.ts` which includes:
- Automatic JWT token management
- Error handling and auth redirects
- Request/response interceptors

## Authentication Flow

1. User signs up or logs in
2. JWT token is stored in localStorage
3. Token is automatically included in all API requests
4. On 401 errors, user is redirected to login
5. Protected routes check authentication before rendering

## Key Features

### Dashboard
- View all generated CVs
- Create new CV with job description
- Download completed CVs as PDF
- Delete CVs
- View CV details (job description, link, model)
- Real-time status updates (polling every 3s for active CVs)

### Settings
- Select AI provider (Google, Groq)
- Select model
- Manage API keys (add, view masked, delete)
- Uses default key if none provided

### Profile (Coming Soon)
- Edit personal information
- Manage CV sections
- Live preview of CV template

## Development Notes

- Uses Mantine v7 components
- Form validation with @mantine/form
- Notifications with @mantine/notifications
- Icons from @tabler/icons-react
- Protected routes with custom ProtectedRoute component
- Global auth state with Context API
- Server state with TanStack Query

## License

MIT
