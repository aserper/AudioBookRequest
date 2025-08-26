# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Setup
```bash
# Install Python dependencies using uv (SQLite support)
uv sync

# For PostgreSQL support, install additional dependencies
uv sync --group postgresql

# Install Node.js dependencies for CSS processing
npm i

# Initialize database (required before first run)
uv run alembic upgrade heads
```

### Development
```bash
# Start FastAPI development server
uv run fastapi dev

# Start Tailwind CSS watcher (required for styling)
uv run tailwindcss -i static/tw.css -o static/globals.css --watch
# Alternative using npx:
npx @tailwindcss/cli@4 -i static/tw.css -o static/globals.css --watch

# Optional: Start browser-sync for hot reload (serves on localhost:3000)
browser-sync http://localhost:8000 --files templates/** --files app/**
```

### Testing and Quality
```bash
# Type checking
uv run pyright

# Linting
uv run ruff check
uv run ruff format

# HTML template linting
uv run djlint templates/
```

### Database Migrations
```bash
# Create new migration after model changes
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade heads
```

### Docker
```bash
# Run locally with Docker Compose (SQLite)
docker compose --profile local up --build

# Run locally with Docker Compose (PostgreSQL)
docker compose --profile postgresql up --build

# Production deployment (single container with SQLite)
docker run -p 8000:8000 -v $(pwd)/config:/config markbeep/audiobookrequest:1

# For PostgreSQL deployments, use docker-compose with postgresql profile
# Copy .env.example to .env and configure database credentials first
```

## Architecture

AudioBookRequest is a FastAPI-based audiobook request management system with the following key components:

### Core Application Structure
- **app/main.py**: FastAPI application entry point with middleware setup and exception handlers
- **app/internal/models.py**: SQLModel database models including User, BookRequest, ManualBookRequest, Config, Notification, APIKey
- **app/internal/env_settings.py**: Pydantic settings management with environment variable support (prefix: `ABR_`)

### Authentication & Authorization
- **app/internal/auth/**: Authentication system supporting multiple login types (basic, forms, OIDC, none)
- User roles: `untrusted` (manual review), `trusted` (auto-download), `admin` (full access)
- Session-based authentication with dynamic middleware
- OIDC integration for external authentication providers

### Router Structure
- **app/routers/**: FastAPI routers organized by functionality
  - `auth.py`: Authentication endpoints
  - `search.py`: Book search functionality  
  - `wishlist.py`: Request management
  - `settings/`: Configuration pages (account, download, indexers, notifications, prowlarr, security, users)
  - `api/`: API endpoints for external access

### Data Models & Business Logic
- **BaseBook**: Core book metadata (ASIN, title, authors, narrators, runtime, etc.)
- **BookRequest**: User book requests with unique ASIN/user constraints
- **ManualBookRequest**: Custom book requests not found in search
- **User**: Authentication with group-based permissions
- **Config**: Key-value configuration storage
- **Notification**: Event-driven notifications (new request, successful/failed download)

### Indexer System
- **app/internal/indexers/**: Abstract indexer framework for book source discovery
- Plugin architecture with `AbstractIndexer` base class
- Integration with Prowlarr for automated downloading
- Support for torrent and usenet sources with metadata enrichment

### External Integrations
- **Prowlarr**: Automated source discovery and downloading
- **Audible API**: Book metadata and search functionality
- **Notification Services**: Webhook-based notifications for events

### Frontend Technology
- **Templates**: Jinja2 templates with HTMX for dynamic interactions
- **Styling**: Tailwind CSS with DaisyUI components
- **JavaScript**: Alpine.js for client-side interactivity

### Database Configuration

#### SQLite (Default)
- Lightweight file-based database
- Ideal for local development and small deployments
- No additional setup required
- Database file stored in `/config/db.sqlite` by default

#### PostgreSQL (Production)
- Robust database for production workloads
- Requires PostgreSQL server installation
- Install dependencies: `uv sync --group postgresql`
- Configure environment variables for connection
- Supports Docker Compose profile: `--profile postgresql`

### Development Notes
- Supports both SQLite (default) and PostgreSQL databases
- Database migrations handled by Alembic
- Pydantic v2 for validation and settings
- Requires Python 3.12+ for modern generics syntax
- Environment variables prefixed with `ABR_` (nested with `__`)
- Configuration stored in `/config` directory by default
- See [DOCKER_USAGE.md](DOCKER_USAGE.md) for detailed Docker configuration