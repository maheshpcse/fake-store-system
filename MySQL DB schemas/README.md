# Fake Store MySQL schema and seed data

These scripts are intended for a local MySQL 8 database opened through SQLyog.

## SQLyog execution order

1. Open and execute `00_create_database.sql`.
2. Open and execute `01_create_all_tables.sql`.
3. Open and execute `02_seed_all_data.sql`.
4. Open and execute `03_verify_database.sql`.

The seed script is generated from every JSON export under
`MongoDB collections/`.

`02_seed_all_data.sql` truncates the Fake Store tables before loading the
sample records. Use it only for local/test databases.

## Normalization notes

- Mongo `_id.$oid` becomes `mongo_id`.
- User nested names become `first_name` and `last_name`.
- User geolocation becomes `latitude` and `longitude`.
- Product rating becomes `rating_rate` and `rating_count`.
- Products reference normalized `categories`.
- Wishlist nested products become `wishlist_items`.
- Cart `id = 6` appears twice in MongoDB. MySQL uses an internal cart `id` and
  preserves the source value as `legacy_id`, uniquely paired with `user_id`.
- Standalone `fake_store.cart_items.json` records are treated as authoritative.
- Mongo passwords are not inserted as plaintext. The generator creates bcrypt
  password hashes.
- File-processing tables are persistent because Lambda retries may continue in
  a different process.

## Local backend environment

Copy `local.env.example` to the project root as `.env` and replace
`YOUR_MYSQL_PASSWORD`:

```powershell
Copy-Item '.\MySQL DB schemas\local.env.example' .env
```

If the password contains characters such as `@`, `:`, `/`, `#`, or `%`, URL
encode it in `DATABASE_URL`.

For example, a password ending in `@` must use `%40`:

```text
DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD%40@127.0.0.1:3306/fake_store
```

Activate the virtual environment and start FastAPI:

```powershell
.\.venv\Scripts\Activate.ps1
python scripts/test_mysql_connection.py
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Local URLs:

```text
Health:       http://127.0.0.1:8000/health
Swagger UI:   http://127.0.0.1:8000/docs
OpenAPI JSON: http://127.0.0.1:8000/openapi.json
```

The seeded login credentials can be taken from the original MongoDB user
export. For example:

```text
Email:    john@gmail.com
Password: m38rmF$
```

Authentication routes expected by the React frontend:

```text
POST /api/v1/auth/signup
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

Allowed frontend development origins:

```text
Angular: http://localhost:4200
React:   http://localhost:3000
Vite:    http://localhost:5173
```

AWS credentials are not required for the health, catalog, or local report
status endpoints. Actual S3/SFTP Lambda execution still requires AWS/SFTP
configuration.

Do not run `alembic upgrade head` after using these SQLyog scripts on the same
database. The current initial Alembic migration overlaps with tables created by
`01_create_all_tables.sql`.
