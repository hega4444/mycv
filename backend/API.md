# myCv Backend API Documentation

Base URL: `http://localhost:3000`

## Authentication

All endpoints except `/auth/signup`, `/auth/login`, `/health`, and `/api/v1/providers` require JWT authentication.

Include the token in the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

---

## Endpoints

### Authentication

#### POST `/api/v1/auth/signup`
Create a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:** `201 Created`
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "email": "user@example.com"
}
```

---

#### POST `/api/v1/auth/login`
Login with email and password.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "eyJhbGci...",
  "token_type": "bearer",
  "email": "user@example.com"
}
```

---

#### POST `/api/v1/auth/logout`
Logout (client should discard token).

**Response:** `204 No Content`

---

#### GET `/api/v1/auth/me`
Get current authenticated user.

**Response:** `200 OK`
```json
{
  "email": "user@example.com"
}
```

---

### Profile & CV Template

#### GET `/api/v1/profile`
Get user's personal data and CV content.

**Response:** `200 OK`
```json
{
  "personal_data": {
    "full_name": "John Doe",
    "job_title": "Senior Software Engineer",
    "email": "john@example.com",
    "phone": "+1234567890",
    "location": "San Francisco, CA",
    "nationality": "American",
    "website": "https://johndoe.com",
    "linkedin": "https://linkedin.com/in/johndoe",
    "github": "https://github.com/johndoe"
  },
  "cv_content": {
    "professional_summary": "Experienced software engineer...",
    "core_competencies": {
      "technical_skills": ["Python", "JavaScript", "React"]
    },
    "professional_experience": [...],
    "education": [...],
    "courses": [...],
    "key_projects": [...],
    "languages": [...]
  }
}
```

---

#### PUT `/api/v1/profile/personal`
Update user's personal data (partial update supported).

**Request:**
```json
{
  "full_name": "John Doe",
  "job_title": "Senior Software Engineer",
  "email": "john@example.com",
  "phone": "+1234567890",
  "location": "San Francisco, CA",
  "nationality": "American",
  "website": "https://johndoe.com",
  "linkedin": "https://linkedin.com/in/johndoe",
  "github": "https://github.com/johndoe"
}
```

**Response:** `204 No Content`

---

#### PUT `/api/v1/profile/content`
Update user's CV content (sections).

**Request:**
```json
{
  "cv_content": {
    "professional_summary": "Updated summary...",
    "core_competencies": {
      "technical_skills": ["Python", "JavaScript", "React", "TypeScript"]
    },
    "professional_experience": [...],
    "education": [...],
    "courses": [...],
    "key_projects": [...],
    "languages": [...]
  }
}
```

**Response:** `204 No Content`

---

#### GET `/api/v1/profile/preview`
Generate HTML preview of CV template.

**Response:** `200 OK`
```json
{
  "html": "<html>...</html>"
}
```

---

### CV Generation

#### GET `/api/v1/cvs`
Get all CVs for the current user.

**Response:** `200 OK`
```json
{
  "cvs": [
    {
      "id": "507f1f77bcf86cd799439011",
      "description": "Senior AI Engineer @ Google",
      "job_description": "Looking for senior AI engineer...",
      "link": "https://jobs.google.com/...",
      "model": "gemini-2.5-flash",
      "provider": "google",
      "status": "completed",
      "cv_optimized": {...},
      "error_message": null,
      "created_at": "2025-10-10T12:00:00Z",
      "updated_at": "2025-10-10T12:05:00Z"
    }
  ]
}
```

---

#### POST `/api/v1/cvs`
Create a new CV and start optimization process.

**Request:**
```json
{
  "description": "Senior AI Engineer @ Google",
  "job_description": "Looking for senior AI engineer with 5+ years experience...",
  "link": "https://jobs.google.com/..."
}
```

**Response:** `201 Created`
```json
{
  "id": "507f1f77bcf86cd799439011",
  "description": "Senior AI Engineer @ Google",
  "job_description": "Looking for senior AI engineer...",
  "link": "https://jobs.google.com/...",
  "model": "gemini-2.5-flash",
  "provider": "google",
  "status": "processing",
  "cv_optimized": null,
  "error_message": null,
  "created_at": "2025-10-10T12:00:00Z",
  "updated_at": "2025-10-10T12:00:00Z"
}
```

---

#### GET `/api/v1/cvs/{cv_id}`
Get a specific CV by ID.

**Response:** `200 OK`
```json
{
  "id": "507f1f77bcf86cd799439011",
  "description": "Senior AI Engineer @ Google",
  "job_description": "Looking for senior AI engineer...",
  "link": "https://jobs.google.com/...",
  "model": "gemini-2.5-flash",
  "provider": "google",
  "status": "completed",
  "cv_optimized": {...},
  "error_message": null,
  "created_at": "2025-10-10T12:00:00Z",
  "updated_at": "2025-10-10T12:05:00Z"
}
```

---

#### DELETE `/api/v1/cvs/{cv_id}`
Delete a CV.

**Response:** `204 No Content`

---

#### GET `/api/v1/cvs/{cv_id}/pdf`
Generate and download PDF for a completed CV.

**Response:** `200 OK` (PDF file download)

---

#### GET `/api/v1/cvs/{cv_id}/status`
Poll CV generation status.

**Response:** `200 OK`
```json
{
  "status": "completed",
  "error_message": null
}
```

Status values: `pending`, `processing`, `completed`, `failed`

---

### Settings

#### GET `/api/v1/settings`
Get user settings.

**Response:** `200 OK`
```json
{
  "provider": "google",
  "model": "gemini-2.5-flash",
  "api_key_display": "•••abc123",
  "has_api_key": true
}
```

---

#### PUT `/api/v1/settings`
Update user settings.

**Request:**
```json
{
  "provider": "google",
  "model": "gemini-2.5-flash",
  "api_key": "your-api-key-here"
}
```

Note: `api_key` is optional. Omit it to keep the existing API key.

**Response:** `204 No Content`

---

#### DELETE `/api/v1/settings/api-key`
Delete the API key for the current provider.

**Response:** `204 No Content`

---

### Providers

#### GET `/api/v1/providers`
Get list of all available AI providers and their models.

**Response:** `200 OK`
```json
{
  "providers": [
    {
      "id": "google",
      "name": "Google",
      "models": [
        {
          "id": "gemini-2.5-flash",
          "name": "Gemini 2.5 Flash"
        },
        {
          "id": "gemini-2.5-flash-lite",
          "name": "Gemini 2.5 Flash-Lite"
        },
        {
          "id": "gemini-2.5-pro",
          "name": "Gemini 2.5 Pro"
        }
      ]
    },
    {
      "id": "groq",
      "name": "Groq",
      "models": [
        {
          "id": "openai/gpt-oss-120b",
          "name": "OpenAI GPT OSS 120B"
        },
        {
          "id": "moonshotai/kimi-k2-instruct-0905",
          "name": "Kimi K2 Instruct"
        }
      ]
    }
  ]
}
```

---

#### GET `/api/v1/providers/{provider_id}/models`
Get list of models for a specific provider.

**Response:** `200 OK`
```json
[
  {
    "id": "gemini-2.5-flash",
    "name": "Gemini 2.5 Flash"
  },
  {
    "id": "gemini-2.5-flash-lite",
    "name": "Gemini 2.5 Flash-Lite"
  },
  {
    "id": "gemini-2.5-pro",
    "name": "Gemini 2.5 Pro"
  }
]
```

---

### Utility

#### GET `/health`
Health check endpoint.

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "service": "myCv Backend API"
}
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - Not authorized to access resource
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## Running the API

```bash
cd backend
uv run python -m src.api.v1.main
```

API will be available at `http://localhost:3000`

Interactive API documentation (Swagger): `http://localhost:3000/docs`
