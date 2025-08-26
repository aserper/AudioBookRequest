# Docker Configuration Guide

AudioBookRequest supports two database backends through Docker Compose profiles:

## Quick Start

### SQLite (Local Development)
```bash
# Start with SQLite database (maintains backward compatibility)
docker-compose --profile local up -d

# Or simply (local profile is included in web service)
docker-compose up web -d
```

### PostgreSQL (Production)
```bash
# Start with PostgreSQL database
docker-compose --profile postgresql up -d

# Stop the services
docker-compose --profile postgresql down
```

## Environment Configuration

### Using Environment Variables
Create a `.env` file from the example:
```bash
cp .env.example .env
```

Edit the `.env` file to customize:
- Database credentials
- Application settings
- Security configuration

### Manual Environment Variables
```bash
# PostgreSQL credentials
export POSTGRES_DB=myapp_db
export POSTGRES_USER=myapp_user  
export POSTGRES_PASSWORD=secure_password_here

# Start with custom configuration
docker-compose --profile postgresql up -d
```

## Service Details

### Services by Profile

**Local Profile (`--profile local`)**:
- `web`: AudioBookRequest application with SQLite
- `gotify`: Notification service

**PostgreSQL Profile (`--profile postgresql`)**:
- `web-postgresql`: AudioBookRequest application with PostgreSQL
- `postgres`: PostgreSQL 16 database server
- `gotify`: Notification service

### Data Persistence

**SQLite Mode**:
- Database stored in `./config/db.sqlite`
- Application data in `./config/`

**PostgreSQL Mode**:
- Database data in Docker volume `postgres_data`
- Application data in `./config/`

## Production Considerations

### Security
1. **Change default passwords** in `.env` file
2. **Limit network exposure** - remove PostgreSQL port mapping if not needed:
   ```yaml
   # Comment out or remove this line in docker-compose.yml
   # - "5432:5432"
   ```
3. **Use strong passwords** for database and admin accounts
4. **Regular backups** of both database and config directory

### Performance
- PostgreSQL is recommended for production workloads
- Adjust PostgreSQL memory settings for your hardware
- Monitor disk space for both database and config volumes

### Monitoring
- PostgreSQL includes health checks
- Check logs: `docker-compose logs web-postgresql postgres`
- Monitor resource usage: `docker stats`

## Troubleshooting

### Common Issues

**PostgreSQL Connection Errors**:
```bash
# Check if PostgreSQL is healthy
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Check database connectivity
docker-compose exec postgres pg_isready -U audiobookrequest
```

**Migration Issues**:
Database migrations now run automatically and are fully compatible with PostgreSQL. If needed, you can run them manually:
```bash
# Run database migrations manually (rarely needed)
docker-compose exec web-postgresql /app/.venv/bin/alembic upgrade heads
```

**Port Conflicts**:
- Change ports in docker-compose.yml if 8000 or 5432 are in use
- Update firewall rules accordingly

### Data Migration

**SQLite to PostgreSQL**:
1. Export data from SQLite instance
2. Set up PostgreSQL instance
3. Import data (manual process - contact support if needed)

**Backup and Restore**:
```bash
# Backup PostgreSQL
docker-compose exec postgres pg_dump -U audiobookrequest audiobookrequest > backup.sql

# Restore PostgreSQL
cat backup.sql | docker-compose exec -T postgres psql -U audiobookrequest audiobookrequest
```

## Development

### Building with PostgreSQL Support
The Dockerfile automatically includes PostgreSQL dependencies (`psycopg2-binary`) for both profiles.

### Local Development
```bash
# Use SQLite for faster local development
docker-compose --profile local up -d

# Use PostgreSQL to match production
docker-compose --profile postgresql up -d
```