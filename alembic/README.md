# Alembic Migrations

## How to generate a new migration:
After making changes to the SQLAlchemy models in `app/models/`, you can auto-generate a migration script by running:

```bash
alembic revision --autogenerate -m "Description of changes"
```

## How to apply migrations:
To apply the generated migrations to the database, run:

```bash
alembic upgrade head
```

## How to revert a migration:
To revert the last applied migration, run:

```bash
alembic downgrade -1
```
