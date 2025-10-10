# myCv - AI-Powered CV Optimizer

Full-stack application for creating and optimizing CVs using AI, tailored to specific job descriptions.

## 🚀 Features

- **AI-Powered Optimization** - Uses Google Gemini or Groq AI to optimize your CV for specific job postings
- **Multiple AI Providers** - Support for Google (Gemini) and Groq
- **CV Management** - Create, track, and manage multiple optimized CVs
- **PDF Generation** - Download optimized CVs as professional PDFs
- **User Authentication** - Secure JWT-based authentication
- **Real-time Status Updates** - Track CV generation progress in real-time
- **Settings Management** - Configure AI providers, models, and API keys

## 📁 Project Structure

```
mycv/
├── backend/          # Python FastAPI backend
│   ├── src/
│   │   ├── api/     # REST API endpoints
│   │   ├── service/ # Business logic
│   │   └── database.py
│   └── API.md       # API documentation
├── frontend/         # React TypeScript frontend
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   └── README.md
└── README.md
```

## 🛠️ Tech Stack

### Backend
- **Python 3.12+**
- **FastAPI** - Modern, fast web framework
- **MongoDB** - Database for user data and CVs
- **JWT** - Authentication
- **Google AI & Groq** - AI providers for CV optimization
- **WeasyPrint** - PDF generation

### Frontend
- **React 18** with TypeScript
- **Vite** - Fast build tool
- **Mantine UI** - Component library
- **React Router** - Navigation
- **TanStack Query** - Server state management
- **Axios** - HTTP client

## 🏃 Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- MongoDB (local or Atlas)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
uv sync
```

3. Create `.env` file:
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=mycv
APP_SECRET_KEY=your-secret-key-here
```

4. Run the backend:
```bash
uv run python -m src.api.v1.main
```

Backend will be available at `http://localhost:3000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env` file:
```env
VITE_API_URL=http://localhost:3000
```

4. Run the frontend:
```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 📖 API Documentation

Full API documentation is available at:
- Backend API docs: `http://localhost:3000/docs` (Swagger UI)
- Written docs: [backend/API.md](backend/API.md)

## 🎯 Usage

1. **Sign up** or **Login** to your account
2. Navigate to **Settings** to configure your AI provider and API key
3. Go to **Dashboard** and click **Create New CV**
4. Paste the job description and add a description
5. Wait for AI optimization to complete (status updates in real-time)
6. **Download PDF** when ready

## 🔐 Environment Variables

### Backend
- `MONGODB_URI` - MongoDB connection string
- `MONGODB_DATABASE` - Database name (default: mycv)
- `APP_SECRET_KEY` - Secret key for encryption
- `STORAGE_SECRET` - Secret for session storage
- `PORT` - API port (default: 3000)
- `ENVIRONMENT` - Environment (development/production)

### Frontend
- `VITE_API_URL` - Backend API URL (default: http://localhost:3000)

## 🏗️ Architecture

### Backend API Endpoints

- **Authentication**: `/api/v1/auth/*`
  - POST `/signup`, `/login`, `/logout`
  - GET `/me`

- **Profile**: `/api/v1/profile`
  - GET `/` - Get personal data and CV content
  - PUT `/personal` - Update personal data
  - PUT `/content` - Update CV content
  - GET `/preview` - Generate HTML preview

- **CVs**: `/api/v1/cvs`
  - GET `/` - List all CVs
  - POST `/` - Create new CV
  - GET `/{cv_id}` - Get specific CV
  - DELETE `/{cv_id}` - Delete CV
  - GET `/{cv_id}/pdf` - Download PDF
  - GET `/{cv_id}/status` - Poll status

- **Settings**: `/api/v1/settings`
  - GET `/` - Get settings
  - PUT `/` - Update settings
  - DELETE `/api-key` - Remove API key

- **Providers**: `/api/v1/providers`
  - GET `/` - List providers
  - GET `/{provider_id}/models` - Get models

### Frontend Pages

- **/login** - User login
- **/signup** - User registration
- **/dashboard** - CV list and management
- **/profile** - Edit CV template (coming soon)
- **/settings** - Configure providers and API keys

## 🔄 CV Generation Flow

1. User creates CV with job description
2. Backend creates CV document with `processing` status
3. Background thread:
   - Loads user's base CV content
   - Sends to AI provider for optimization
   - Updates CV with results
4. Frontend polls status every 3 seconds
5. User downloads PDF when `completed`

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT

## 🙏 Acknowledgments

- Built with FastAPI and React
- AI powered by Google Gemini and Groq
- UI components from Mantine
