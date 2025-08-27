---
title: 'Environment Variables'
description: >
  List of the environment variables that can be set.
date: 2025-06-09T13:46:33+02:00
---

| ENV                           | Description                                                                                                                                                                                                                                                  | Default   |
| ----------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------- |
| `ABR_APP__PORT`               | The port to run the server on.                                                                                                                                                                                                                               | 8000      |
| `ABR_APP__DEBUG`              | If to enable debug mode. Not recommended for production.                                                                                                                                                                                                     | false     |
| `ABR_APP__OPENAPI_ENABLED`    | If set to `true`, enables an OpenAPI specs page on `/docs`.                                                                                                                                                                                                  | false     |
| `ABR_APP__CONFIG_DIR`         | The directory path where persistant data and configuration is stored. If ran using Docker or Kubernetes, this is the location a volume should be mounted to.                                                                                                 | /config   |
| `ABR_APP__LOG_LEVEL`          | One of `DEBUG`, `INFO`, `WARN`, `ERROR`.                                                                                                                                                                                                                     | INFO      |
| `ABR_APP__BASE_URL`           | Defines the base url the website is hosted at. If the website is accessed at `example.org/abr/`, set the base URL to `/abr/`                                                                                                                                 |           |
| `ABR_DB__TYPE`                | Database type to use. Can be `sqlite` or `postgresql`.                                                                                                                                                                                                       | sqlite    |
| `ABR_DB__SQLITE_PATH`         | If relative, path and name of the sqlite database in relation to `ABR_APP__CONFIG_DIR`. If absolute (path starts with `/`), the config dir is ignored and only the absolute path is used. Only used when `ABR_DB__TYPE` is `sqlite`.                    | db.sqlite |
| `ABR_DB__POSTGRESQL__HOST`    | PostgreSQL database host. Only used when `ABR_DB__TYPE` is `postgresql`.                                                                                                                                                                                     | localhost |
| `ABR_DB__POSTGRESQL__PORT`    | PostgreSQL database port. Only used when `ABR_DB__TYPE` is `postgresql`.                                                                                                                                                                                     | 5432      |
| `ABR_DB__POSTGRESQL__USER`    | PostgreSQL database user. Only used when `ABR_DB__TYPE` is `postgresql`.                                                                                                                                                                                     | postgres  |
| `ABR_DB__POSTGRESQL__PASSWORD`| PostgreSQL database password. Only used when `ABR_DB__TYPE` is `postgresql`.                                                                                                                                                                                 |           |
| `ABR_DB__POSTGRESQL__DATABASE`| PostgreSQL database name. Only used when `ABR_DB__TYPE` is `postgresql`.                                                                                                                                                                                     | audiobookrequest |
| `ABR_APP__DEFAULT_REGION`     | Default audible region to use for the search. Has to be one of `us, ca, uk, au, fr, de, jp, it, in, es, br`.                                                                                                                                                 | us        |
| `ABR_APP__FORCE_LOGIN_TYPE`   | Forces the login type and prevents it from being modified. Can be one of `basic`, `forms`, `oidc`, or `none` to disable the login. `oidc` requires both the `ABR_APP__INIT_ROOT_USERNAME` and `ABR_APP__INIT_ROOT_PASSWORD` environment variables to be set. |           |
| `ABR_APP__INIT_ROOT_USERNAME` | Sets the initial username of the root user when first launching ABR. Has no effect if a root admin already exists.                                                                                                                                           |           |
| `ABR_APP__INIT_ROOT_PASSWORD` | Sets the initial password of the root user when first launching ABR. Has no effect if a root admin already exists.                                                                                                                                           |           |

{{< alert title="Note" >}} There are two underscores (`__`) between the first
and second part of each environment variable like between `ABR_APP` and `PORT`.
{{< /alert >}}

{{< alert title="PostgreSQL Support" >}} To use PostgreSQL as the database backend, you need to install the PostgreSQL dependencies. If using uv, run `uv sync --group postgresql` to install the required packages. When using PostgreSQL, make sure the database exists and is accessible before starting the application. Database migrations are compatible and run automatically. {{< /alert >}}

## Configuration Examples

### SQLite Configuration (Default)
```bash
# Minimal configuration for SQLite (default)
ABR_DB__TYPE=sqlite
ABR_DB__SQLITE_PATH=db.sqlite
```

### PostgreSQL Configuration
```bash
# PostgreSQL database configuration
ABR_DB__TYPE=postgresql
ABR_DB__POSTGRESQL__HOST=localhost
ABR_DB__POSTGRESQL__PORT=5432
ABR_DB__POSTGRESQL__USER=audiobookrequest
ABR_DB__POSTGRESQL__PASSWORD=your_secure_password
ABR_DB__POSTGRESQL__DATABASE=audiobookrequest
```

### Docker Environment Files

For Docker deployments, copy `.env.example` to `.env` and customize:

```bash
# Copy the example file
cp .env.example .env

# Edit with your settings
vim .env
```

## Common Issues

### PostgreSQL Connection Problems

1. **Database doesn't exist**: Create the database before starting AudioBookRequest:
   ```sql
   CREATE DATABASE audiobookrequest;
   ```

2. **Permission denied**: Ensure the PostgreSQL user has proper permissions:
   ```sql
   GRANT ALL PRIVILEGES ON DATABASE audiobookrequest TO audiobookrequest;
   ```

3. **Connection refused**: Verify PostgreSQL is running and accessible on the specified host/port.

4. **Authentication failed**: Check that the username and password are correct.

### Migration Issues

Database migrations are compatible with both SQLite and PostgreSQL. Migrations run automatically in most cases, but can be run manually if needed:

```bash
# Apply all pending migrations (rarely needed)
uv run alembic upgrade heads
```
