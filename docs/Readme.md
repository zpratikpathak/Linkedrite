<div align="center">
  <img src="icon.png" alt="Linkedrite">
</div>

LinkedRite is an AI-powered LinkedIn post rewriter that helps you craft professional, engaging posts. It corrects grammar, generates relatable context, adds emojis, formats your post, and more. Use it via the [web app](https://linkedrite.pratikpathak.com) or the Chrome extension.

## Features

- **AI Rewriting** -- Rewrites your LinkedIn posts to be more professional and engaging
- **Grammar Correction** -- Fixes grammatical errors automatically
- **Emoji Support** -- Adds relevant emojis to boost engagement
- **Hashtag Generation** -- Adds relevant hashtags for visibility
- **User Accounts** -- Sign up, email verification, and profile management
- **Subscription Plans** -- Free (20 rewrites/day) and Premium (unlimited) tiers
- **Usage Tracking** -- Timezone-aware daily limits with dashboard analytics
- **Multi-Provider AI** -- Supports Google Gemini and Azure OpenAI (configurable via env)

## Tech Stack

- **Backend:** Django 5.2, Django REST Framework
- **AI:** Google Gemini (`google-genai`) / Azure OpenAI (`openai`)
- **Frontend:** Tailwind CSS (CDN), Alpine.js
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Cache:** Redis (optional)
- **Deployment:** Docker, Docker Compose, GitHub Actions

## Quick Start

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Installation

```bash
git clone https://github.com/zpratikpathak/Linkedrite.git
cd Linkedrite
uv sync
```

### Environment Setup

Copy the example env file and fill in your values:

```bash
cp .env.example .env
```

Key variables to set:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

AI_PROVIDER=google
GOOGLE_API_KEY=your-google-gemini-api-key
GOOGLE_MODEL=gemini-3-flash-preview

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=LinkedRite <noreply@yourdomain.com>
```

See `.env.example` for all available options including Azure OpenAI, database, Redis, and admin account configuration.

### Run Locally

```bash
uv run python manage.py migrate
uv run python manage.py runserver
```

The app will be available at `http://localhost:8000`.

### Create Admin User (Optional)

Add these to your `.env` and the admin account will be created automatically on first request:

```env
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=your-secure-password
```

Or run manually:

```bash
uv run python manage.py create_default_admin
```

## Production Deployment

### Docker Compose

```bash
docker-compose up -d
```

This starts the web app (port 8009), PostgreSQL, and Redis.

### Production `.env`

For production, make sure to set:

```env
SECRET_KEY=a-long-random-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SITE_URL=https://yourdomain.com
USE_HTTPS=True
```

## Chrome Extension

The `ChromeExtension/` directory contains a Chrome extension that integrates LinkedRite directly into the LinkedIn post editor.

## License

ISC
