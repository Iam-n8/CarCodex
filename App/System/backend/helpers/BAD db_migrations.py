# --------------------------------------------------
# db_migrations.py
#
# Maintain Hub Database Migration System
#
# Purpose:
# - Track database schema changes
# - Apply migrations in a defined order
# - Preserve existing user data
# - Prevent future full database resets
# --------------------------------------------------

from datetime import datetime

from sqlalchemy import (
    inspect,
    text
)

from database import (
    engine
)


# --------------------------------------------------
# Migration Tracking Table
# --------------------------------------------------

def ensure_migration_table():
    """
    Create the schema_migrations table if it does
    not already exist.
    """

    statement = text(
        """
        CREATE TABLE IF NOT EXISTS schema_migrations (
            migration_id TEXT PRIMARY KEY,
            migration_name TEXT NOT NULL,
            applied_at TEXT NOT NULL
        )
        """
    )

    with engine.begin() as connection:

        connection.execute(
            statement
        )


# --------------------------------------------------
# Table Inspection
# --------------------------------------------------

def table_exists(
    table_name: str
) -> bool:
    """
    Return True if a database table exists.
    """

    inspector = inspect(
        engine
    )

    return inspector.has_table(
        table_name
    )


# --------------------------------------------------
# Column Inspection
# --------------------------------------------------

def column_exists(
    table_name: str,
    column_name: str
) -> bool:
    """
    Return True if a column exists in a table.
    """

    if not table_exists(
        table_name
    ):

        return False

    inspector = inspect(
        engine
    )

    columns = inspector.get_columns(
        table_name
    )

    for column in columns:

        if column["name"] == column_name:

            return True

    return False


# --------------------------------------------------
# Add Column If Missing
# --------------------------------------------------

def add_column_if_missing(
    connection,
    table_name: str,
    column_name: str,
    column_definition: str
) -> bool:
    """
    Add a column only when the column does not exist.

    Returns True when a column was added.
    Returns False when the column already existed.
    """

    if column_exists(
        table_name,
        column_name
    ):

        print(
            f"Migration check: "
            f"{table_name}.{column_name} already exists"
        )

        return False

    statement = text(
        f"""
        ALTER TABLE {table_name}
        ADD COLUMN {column_name} {column_definition}
        """
    )

    connection.execute(
        statement
    )

    print(
        f"Migration added: "
        f"{table_name}.{column_name}"
    )

    return True


# --------------------------------------------------
# Applied Migration Check
# --------------------------------------------------

def migration_applied(
    migration_id: str
) -> bool:
    """
    Return True if a migration has already been applied.
    """

    ensure_migration_table()

    statement = text(
        """
        SELECT migration_id
        FROM schema_migrations
        WHERE migration_id = :migration_id
        """
    )

    with engine.connect() as connection:

        result = connection.execute(
            statement,
            {
                "migration_id": migration_id
            }
        ).first()

    return result is not None


# --------------------------------------------------
# Record Applied Migration
# --------------------------------------------------

def record_migration(
    connection,
    migration_id: str,
    migration_name: str
):
    """
    Record a successfully applied migration.
    """

    statement = text(
        """
        INSERT INTO schema_migrations (
            migration_id,
            migration_name,
            applied_at
        )
        VALUES (
            :migration_id,
            :migration_name,
            :applied_at
        )
        """
    )

    connection.execute(
        statement,
        {
            "migration_id": migration_id,
            "migration_name": migration_name,
            "applied_at": datetime.now().isoformat(
                timespec="seconds"
            )
        }
    )
# --------------------------------------------------
# Migration 002: Service Catalog Fields
# --------------------------------------------------

def migration_002_service_catalog_fields(
    connection
):
    """
    Add proper Service Catalog fields.

    Existing display_order fields remain temporarily
    for backward compatibility and page sorting.
    """

    if not table_exists(
        "service_groups"
    ):

        raise RuntimeError(
            "Migration 002 requires the "
            "service_groups table."
        )

    if not table_exists(
        "service_items"
    ):

        raise RuntimeError(
            "Migration 002 requires the "
            "service_items table."
        )

    # ----------------------------------------------
    # Service Group Fields
    # ----------------------------------------------

    add_column_if_missing(
        connection,
        "service_groups",
        "domain",
        "TEXT"
    )

    add_column_if_missing(
        connection,
        "service_groups",
        "group_code",
        "INTEGER"
    )

    add_column_if_missing(
        connection,
        "service_groups",
        "notes",
        "TEXT"
    )

    # ----------------------------------------------
    # Service Item Fields
    # ----------------------------------------------

    add_column_if_missing(
        connection,
        "service_items",
        "domain",
        "TEXT"
    )

    add_column_if_missing(
        connection,
        "service_items",
        "service_code",
        "INTEGER"
    )

    add_column_if_missing(
        connection,
        "service_items",
        "service_category",
        "TEXT"
    )

    add_column_if_missing(
        connection,
        "service_items",
        "track_for_maintenance_due",
        "BOOLEAN DEFAULT 0"
    )

    add_column_if_missing(
        connection,
        "service_items",
        "default_miles_interval",
        "INTEGER"
    )

    add_column_if_missing(
        connection,
        "service_items",
        "default_period_months",
        "INTEGER"
    )

# --------------------------------------------------
# Initial Baseline Migration
# --------------------------------------------------

def migration_001_initial_baseline(
    connection
):
    """
    Mark the current Maintain Hub development schema
    as the initial migration baseline.

    No schema changes occur in this migration.
    """

    print(
        "Migration 001: "
        "Current schema accepted as initial baseline"
    )


# --------------------------------------------------
# Migration Registry
# --------------------------------------------------

MIGRATIONS = [
    {
        "id": "001",
        "name": "initial_baseline",
        "function": migration_001_initial_baseline
    },
    {
        "id": "002",
        "name": "service_catalog_fields",
        "function": migration_002_service_catalog_fields
    }
]


# --------------------------------------------------
# Run Database Migrations
# --------------------------------------------------

def run_database_migrations():
    """
    Run all pending database migrations in order.
    """

    print(
        "Maintain Hub database migrations starting..."
    )

    ensure_migration_table()

    for migration in MIGRATIONS:

        migration_id = migration["id"]

        migration_name = migration["name"]

        migration_function = migration["function"]

        if migration_applied(
            migration_id
        ):

            print(
                f"Migration {migration_id} "
                f"already applied: {migration_name}"
            )

            continue

        print(
            f"Applying migration {migration_id}: "
            f"{migration_name}"
        )

        try:

            with engine.begin() as connection:

                migration_function(
                    connection
                )

                record_migration(
                    connection,
                    migration_id,
                    migration_name
                )

        except Exception as error:

            print(
                f"Migration {migration_id} failed: "
                f"{migration_name}"
            )

            print(
                "Migration error:",
                error
            )

            raise

        print(
            f"Migration {migration_id} complete: "
            f"{migration_name}"
        )

    print(
        "Maintain Hub database migrations complete."
    )
