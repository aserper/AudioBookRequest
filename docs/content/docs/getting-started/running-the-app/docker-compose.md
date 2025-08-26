---
title: 'Docker Compose'
date: 2025-06-09T13:03:35+02:00
description: >
  How to get started using Docker-Compose.
categories: [Setup]
tags: [docker]
weight: 2
---

Docker-compose works the similar way as [Docker](./docker.md), but AudioBookRequest provides two different deployment profiles to choose from based on your database needs.

## Database Profiles

AudioBookRequest supports two Docker Compose profiles:

### SQLite Profile (Local Development)

The SQLite profile uses a lightweight file-based database, ideal for development and small deployments:

```bash
# Start with SQLite database
docker compose --profile local up -d
```

Basic SQLite configuration:

```yaml
services:
  web:
    image: markbeep/audiobookrequest:1
    ports:
      - '8000:8000'
    volumes:
      - ./config:/config
    profiles:
      - local
```

### PostgreSQL Profile (Production)

The PostgreSQL profile includes a PostgreSQL database server for production deployments:

```bash
# Start with PostgreSQL database
docker compose --profile postgresql up -d
```

The PostgreSQL profile includes both the application and database services with proper health checks and networking.

## Environment Configuration

For production PostgreSQL deployments:

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your database credentials:
   ```bash
   # PostgreSQL Configuration
   POSTGRES_DB=audiobookrequest
   POSTGRES_USER=audiobookrequest
   POSTGRES_PASSWORD=your_secure_password_here
   
   # Application PostgreSQL settings
   ABR_DB__TYPE=postgresql
   ABR_DB__POSTGRESQL__HOST=postgres
   ABR_DB__POSTGRESQL__PASSWORD=your_secure_password_here
   ```

3. Start the services:
   ```bash
   docker compose --profile postgresql up -d
   ```

## Custom Environment Variables

You can add additional environment variables as explained
[here](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/).

Example custom configuration:

```yaml
services:
  web:
    image: markbeep/audiobookrequest:1
    ports:
      - '8000:8000'
    volumes:
      - ./config:/config
    environment:
      ABR_APP__PORT: 8000
      ABR_APP__OPENAPI_ENABLED: true
      ABR_APP__LOG_LEVEL: DEBUG
    profiles:
      - local
```

## Advanced Configuration

For detailed configuration options, database management, and troubleshooting, see [DOCKER_USAGE.md](../../../DOCKER_USAGE.md) in the project root.
