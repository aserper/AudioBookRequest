---
title: Local Development
description: How to set up the project for local development.
categories: [Development]
tags: [local]
weight: 9
---

## Requirements

- Python >3.12
- [uv](https://docs.astral.sh/uv/). Used as the package manager
- node.js. Exact version is not too important. Too old versions might fail when
  installing packages.

## Setup

Virtual environments help isolate any installed packages to this directory.
Project was made with `Python 3.12` and uses new generics introduced in 3.12.
Older python versions might not work or could have incorrect typing.

For improved dependency management, `uv` is used instead of `pip`.

```sh
# This creates the venv as well as installs all dependencies (SQLite support)
uv sync

# For PostgreSQL support, install additional dependencies
uv sync --group postgresql
```

For local development, environment variables can be added to `.env.local` and
they'll be used wherever required. This file is not used in production.

## Database Configuration

### SQLite (Default)

SQLite is the default database and requires no additional setup. The database file will be created automatically in your config directory.

### PostgreSQL (Optional)

To use PostgreSQL for local development:

1. Install and start PostgreSQL on your system
2. Create a development database:
   ```sql
   CREATE DATABASE audiobookrequest_dev;
   CREATE USER abr_dev WITH ENCRYPTED PASSWORD 'dev_password';
   GRANT ALL PRIVILEGES ON DATABASE audiobookrequest_dev TO abr_dev;
   ```
3. Install PostgreSQL dependencies:
   ```sh
   uv sync --group postgresql
   ```
4. Configure your `.env.local` file:
   ```bash
   ABR_DB__TYPE=postgresql
   ABR_DB__POSTGRESQL__HOST=localhost
   ABR_DB__POSTGRESQL__PORT=5432
   ABR_DB__POSTGRESQL__USER=abr_dev
   ABR_DB__POSTGRESQL__PASSWORD=dev_password
   ABR_DB__POSTGRESQL__DATABASE=audiobookrequest_dev
   ```

## Initialize Database

[Alembic](https://alembic.sqlalchemy.org/en/latest/) is used to create database
migrations. Run the following before starting up the application for the first
time. It will initialize the directory if non-existant, create the database file
as well as execute any required migrations.

```sh
uv run alembic upgrade heads
```

_In case of any model changes, remember to create migrations using
`alembic revision --autogenerate -m "<message>"`._

## Generate the CSS files

[Tailwindcss](https://tailwindcss.com/) is used to style elements using CSS. On
top of that, [daisyUI](https://daisyui.com/) is for easy and consistent
component styling.

Install daisyUI and start Tailwindcss watcher. Required for any CSS styling.

```sh
npm i
uv run tailwindcss -i static/tw.css -o static/globals.css --watch
# Alternatively npx can be used to run tailwindcss
npx @tailwindcss/cli@4 -i static/tw.css -o static/globals.css --watch
```

Tailwind has to run anytime something is changed in the HTML template files.

## Run the app

Running the application is best done in multiple terminals:

1.  Start FastAPI dev mode:

    ```sh
    uv run fastapi dev
    ```

    Website can be visited at http://localhost:8000.

2.  _Optional:_ Start browser-sync. This hot reloads the website when the html
    template or python files are modified:

```sh
browser-sync http://localhost:8000 --files templates/** --files app/**
```

**NOTE**: Website has to be visited at http://localhost:3000 instead.

## Docker Compose

The docker compose can also be used to run the app locally. Any services that
are required can be added to it for easy testing.

### SQLite Development
```bash
# Run with SQLite database (lightweight for development)
docker compose --profile local up --build
```

### PostgreSQL Development
```bash
# Run with PostgreSQL database (matches production setup)
docker compose --profile postgresql up --build
```

The PostgreSQL profile automatically sets up both the application and a PostgreSQL database server with proper networking and health checks. This is useful for:

- Testing PostgreSQL-specific features
- Matching production database setup
- Development scenarios requiring more robust database features

For PostgreSQL development, you can customize database credentials by copying `.env.example` to `.env` and modifying the values.
