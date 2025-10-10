# MyCV - AI-Powered CV Generator

A web-based application that generates tailored, ATS-optimized CVs using AI. Built with NiceGUI and MongoDB, it allows users to optimize their CV content for specific job descriptions using multiple AI providers.

## Features

### Core Functionality
- **AI-Powered CV Optimization**: Automatically tailors your CV content to match specific job descriptions
- **Multi-Provider AI Support**: Choose between Google Gemini and Groq models
- **ATS-Optimized Output**: Generates clean, parser-friendly HTML and PDF formats
- **Template-Based Generation**: Uses Jinja2 templates for consistent, professional formatting

### User Management
- **Secure Authentication**: User signup and login with bcrypt password hashing
- **Encrypted API Keys**: Store your AI provider API keys securely with encryption
- **Per-User Settings**: Configure AI provider, model, and API keys individually

### CV Management
- **Multiple CVs**: Create and manage multiple tailored CVs for different positions
- **Job Tracking**: Associate CVs with job descriptions and optional job posting links
- **Status Tracking**: Monitor CV generation progress (pending, processing, completed, failed)
- **PDF Export**: Generate and download professional PDFs from optimized CVs

### Background Processing
- **Async CV Generation**: CVs are generated in background tasks without blocking the UI
- **Auto-Refresh**: Dashboard automatically refreshes when CV generation completes
- **Error Handling**: Failed CVs display error messages with retry capability

## Tech Stack

- **Backend**: Python 3.12+
- **Web Framework**: NiceGUI 3.0+
- **Database**: MongoDB (with Motor for async operations)
- **AI**: Pydantic AI with support for Google Gemini and Groq
- **PDF Generation**: WeasyPrint
- **Templating**: Jinja2
- **Security**: bcrypt, cryptography

## Installation

### Prerequisites
- Python 3.12 or higher
- MongoDB instance (local or cloud)
- API key for at least one AI provider (Google Gemini or Groq)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mycv
   ```

2. **Install dependencies**
   ```bash
   uv sync
   ```

3. **Configure environment variables**
   Create a `.env` file in the project root:
   ```env
   # MongoDB Configuration
   MONGODB_URI=mongodb://localhost:27017
   MONGODB_DB=mycv

   # Encryption (generate a secure key)
   ENCRYPTION_KEY=<your-32-byte-base64-encoded-key>

   # Optional: Default API keys (users can override in settings)
   GOOGLE_API_KEY=<your-google-api-key>
   GROQ_API_KEY=<your-groq-api-key>
   ```

4. **Generate encryption key**
   ```python
   from cryptography.fernet import Fernet
   print(Fernet.generate_key().decode())
   ```

5. **Prepare CV data**

   Create your CV data files in the `data/` directory using the provided examples as templates:
   - Copy `cv_personal_data_example.json` to `personal_data.json` and fill in your contact information
   - Copy `cv_content_example.json` to `cv_content.json` and add your professional experience, skills, education, etc.

   The example files include detailed comments explaining each field's structure and purpose.

## Usage

### Start the Application

```bash
uv run python -m src.app.main
```

The application will be available at `http://localhost:8080`

### First Time Setup

1. **Sign up** for an account at `/signup`
2. **Log in** with your credentials
3. **Configure AI settings** (click settings icon in header):
   - Select AI provider (Google or Groq)
   - Choose model
   - Add your API key (optional if default keys are configured)

### Creating a CV

1. Click **"Create New"** on the dashboard
2. Enter:
   - **Description**: Brief identifier (e.g., "Senior AI Engineer @ TechCorp")
   - **Job Description**: Paste the target job posting
   - **Link** (optional): URL to the job posting
3. Click **"Generate"**
4. Wait for processing to complete (status updates automatically)
5. View details, open PDF, or delete completed CVs

## Project Structure

```
mycv/
├── src/
│   ├── app/
│   │   ├── main.py              # NiceGUI application entry point
│   │   ├── auth.py              # Login and signup pages
│   │   ├── dashboard.py         # Main dashboard UI
│   │   ├── background.py        # Async CV processing
│   │   ├── styles.py            # Global CSS styles
│   │   └── styles.css           # Additional CSS styles
│   ├── database.py              # MongoDB operations
│   ├── service/
│   │   ├── cv_generator.py      # PDF/HTML generation
│   │   ├── ai_optimizer.py      # AI-powered CV optimization
|   |   └── providers.py         # LLM API Providers
│   └── models.py                # Pydantic models
├── data/
│   ├── cv_personal_data_example.json  # Example personal information template
│   ├── cv_content_example.json        # Example CV content template
│   ├── personal_data.json             # Your personal information (create from example)
│   ├── cv_content.json                # Your CV content (create from example)
│   └── templates/
│       └── cv_template.html           # Jinja2 CV template
└── output/                      # Generated PDFs (auto-created)
```

## AI Providers

### Supported Providers

**Google Gemini**
- gemini-2.5-flash
- gemini-2.5-flash-lite
- gemini-2.5-pro

**Groq**
- openai/gpt-oss-120b
- moonshotai/kimi-k2-instruct-0905

### Adding New Providers

Edit `src/llm_providers.py`:

```python
PROVIDERS = {
    "new_provider": {
        "name": "Provider Display Name",
        "models": [
            {"id": "model-id", "name": "Model Display Name"},
        ],
    },
}
```

## Database Schema

### Collections

**users**
- `email` (unique): User email
- `password_hash`: Bcrypt hashed password
- `provider`: Selected AI provider
- `model`: Selected AI model

**api_keys**
- `user_email`: User email
- `provider`: AI provider name
- `encrypted_key`: Fernet encrypted API key
- `last_chars`: Last 4 characters for display

**cvs**
- `user_email`: Owner email
- `description`: CV description
- `job_description`: Target job posting
- `link`: Optional job posting URL
- `status`: pending | processing | completed | failed
- `cv_optimized`: Generated CV content (JSON)
- `error_message`: Error details if failed
- `created_at`: Timestamp

## Security

- Passwords are hashed using bcrypt
- API keys are encrypted using Fernet (symmetric encryption)
- Environment variables for sensitive configuration
- User isolation for all database operations

## Development

### Running in Development

```bash
# With hot reload
uv run python -m src.app.main
```

### Linting

```bash
uv run flake8 src/
```

## License

[Your License Here]
