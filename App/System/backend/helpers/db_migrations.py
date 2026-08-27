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

from helpers.service_catalog_loader import (
    load_vehicle_service_catalog_rows,
    clean_csv_value,
    csv_int,
    csv_bool
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
# Migration 001: Initial Baseline
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
# Migration 003: Populate Service Catalog Fields
# --------------------------------------------------

def migration_003_populate_service_catalog_fields(
    connection
):
    """
    Populate the new Service Catalog database fields
    from the Vehicle domain in ServiceCatalog.csv.

    Existing records are matched using:

    ServiceGroup.display_order = CSV group_code
    ServiceItem.display_order = CSV service_code
    """

    if not table_exists(
        "service_groups"
    ):

        raise RuntimeError(
            "Migration 003 requires the "
            "service_groups table."
        )

    if not table_exists(
        "service_items"
    ):

        raise RuntimeError(
            "Migration 003 requires the "
            "service_items table."
        )

    catalog_rows = load_vehicle_service_catalog_rows()

    group_rows_updated = 0

    item_rows_updated = 0

    processed_group_keys = set()

    for row in catalog_rows:

        domain = clean_csv_value(
            row.get(
                "domain"
            )
        )

        group_code = csv_int(
            row.get(
                "group_code"
            ),
            default=0
        )

        group_name = clean_csv_value(
            row.get(
                "group_name"
            )
        )

        service_code = csv_int(
            row.get(
                "service_code"
            ),
            default=0
        )

        service_item = clean_csv_value(
            row.get(
                "service_item"
            )
        )

        service_category = clean_csv_value(
            row.get(
                "service_category"
            )
        )

        track_for_maintenance_due = csv_bool(
            row.get(
                "track_for_maintenance_due"
            )
        )

        default_miles_interval = csv_int(
            row.get(
                "default_miles_interval"
            ),
            default=0
        )

        default_period_months = csv_int(
            row.get(
                "default_period_months"
            ),
            default=0
        )

        notes = clean_csv_value(
            row.get(
                "notes"
            )
        )

        if (
            not domain
            or not group_name
            or not service_item
            or group_code == 0
            or service_code == 0
        ):

            continue

# --------------------------------------------------
# Migration 004: Unique Service Catalog Codes
# --------------------------------------------------

def migration_004_unique_service_catalog_codes(
    connection
):
    """
    Add unique indexes for Service Catalog codes.

    Group identity:
    domain + group_code

    Service item identity:
    domain + service_code

    The same numeric code may be reused in another
    domain, but it must be unique within its domain.
    """

    if not table_exists(
        "service_groups"
    ):

        raise RuntimeError(
            "Migration 004 requires the "
            "service_groups table."
        )

    if not table_exists(
        "service_items"
    ):

        raise RuntimeError(
            "Migration 004 requires the "
            "service_items table."
        )

# --------------------------------------------------
# Migration 005: Vehicle Acquisition Baseline
# --------------------------------------------------

def migration_005_vehicle_acquisition_baseline(
    connection
):
    """
    Add the vehicle acquisition baseline fields used
    by Maintenance Due when no matching completed
    service history exists.

    UI meaning:

    date_acquired:
        Date of Sale / In-Service

    mileage_at_acquisition:
        Mileage at Sale / Acquisition

    vehicle_condition:
        New or Used
    """

    if not table_exists(
        "vehicles"
    ):

        raise RuntimeError(
            "Migration 005 requires the "
            "vehicles table."
        )

    add_column_if_missing(
        connection,
        "vehicles",
        "date_acquired",
        "TEXT"
    )

    add_column_if_missing(
        connection,
        "vehicles",
        "mileage_at_acquisition",
        "INTEGER"
    )

    add_column_if_missing(
        connection,
        "vehicles",
        "vehicle_condition",
        "TEXT"
    )
# --------------------------------------------------
# Migration 006: Vehicle Purchase and Sale Prices
# --------------------------------------------------

def migration_006_vehicle_purchase_and_sale_prices(
    connection
):
    """
    Add optional vehicle purchase and sale prices.

    Values are stored as integer cents to avoid
    floating-point currency errors.

    Examples:

    Purchase price:
    $38,500.00 becomes 3850000 cents

    Sold price:
    $42,000.00 becomes 4200000 cents
    """

    if not table_exists(
        "vehicles"
    ):

        raise RuntimeError(
            "Migration 006 requires the "
            "vehicles table."
        )

    add_column_if_missing(
        connection,
        "vehicles",
        "purchase_price_cents",
        "INTEGER"
    )

    add_column_if_missing(
        connection,
        "vehicles",
        "sold_price_cents",
        "INTEGER"
    )

# --------------------------------------------------
# Migration 007: Vendor Details
# --------------------------------------------------

def migration_007_vendor_details(
    connection
):
    """
    Add structured location, domain, and rating fields
    to the Vendor table.

    Existing address_1 remains the street Address
    field for backward compatibility.

    New fields:

    city:
        Vendor city.

    state:
        Vendor state or region.

    zip_code:
        Vendor ZIP or postal code.

    domain:
        Primary Maintain Hub domain served by the
        vendor, such as Vehicle or House.

    rating:
        Optional numeric rating from 1 through 5.
    """

    if not table_exists(
        "vendors"
    ):

        raise RuntimeError(
            "Migration 007 requires the "
            "vendors table."
        )

    add_column_if_missing(
        connection,
        "vendors",
        "city",
        "TEXT"
    )

    add_column_if_missing(
        connection,
        "vendors",
        "state",
        "TEXT"
    )

    add_column_if_missing(
        connection,
        "vendors",
        "zip_code",
        "TEXT"
    )

    add_column_if_missing(
        connection,
        "vendors",
        "domain",
        "TEXT"
    )

    add_column_if_missing(
        connection,
        "vendors",
        "rating",
        "INTEGER"
    )
# --------------------------------------------------
# Migration 008: Maintenance Visit Vendor ID
# --------------------------------------------------

def migration_008_maintenance_visit_vendor_id(
    connection
):
    """
    Add a durable Vendor relationship to maintenance
    visits.

    The existing vendor text field remains as a
    historical vendor-name snapshot.

    vendor_id:
        References the Vendor record used for the
        maintenance visit.

    Existing rows remain valid because vendor_id
    is optional until the backfill migration runs.
    """

    if not table_exists(
        "maintenance_visits"
    ):

        raise RuntimeError(
            "Migration 008 requires the "
            "maintenance_visits table."
        )

    add_column_if_missing(
        connection,
        "maintenance_visits",
        "vendor_id",
        "INTEGER"
    )
# --------------------------------------------------
# Migration 009: Backfill Maintenance Visit Vendor IDs
# --------------------------------------------------

def migration_009_backfill_maintenance_visit_vendor_ids(
    connection
):
    """
    Populate maintenance_visits.vendor_id for older
    visits by matching the saved vendor-name snapshot
    to an existing Vendor record.

    Matching is:
    - Case-insensitive
    - Whitespace-trimmed
    - Exact after normalization

    Visits without a unique matching Vendor remain
    unchanged with vendor_id set to NULL.
    """

    if not table_exists(
        "maintenance_visits"
    ):

        raise RuntimeError(
            "Migration 009 requires the "
            "maintenance_visits table."
        )

    if not table_exists(
        "vendors"
    ):

        raise RuntimeError(
            "Migration 009 requires the "
            "vendors table."
        )

    updated_result = connection.execute(
        text(
            """
            UPDATE maintenance_visits
            SET vendor_id = (
                SELECT vendors.id
                FROM vendors
                WHERE
                    LOWER(TRIM(vendors.name)) =
                    LOWER(TRIM(maintenance_visits.vendor))
                LIMIT 1
            )
            WHERE
                vendor_id IS NULL
                AND vendor IS NOT NULL
                AND TRIM(vendor) != ''
                AND (
                    SELECT COUNT(*)
                    FROM vendors
                    WHERE
                        LOWER(TRIM(vendors.name)) =
                        LOWER(TRIM(maintenance_visits.vendor))
                ) = 1
            """
        )
    )

    updated_count = updated_result.rowcount

    unmatched_count = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM maintenance_visits
            WHERE
                vendor_id IS NULL
                AND vendor IS NOT NULL
                AND TRIM(vendor) != ''
            """
        )
    ).scalar_one()

    print(
        "Migration 009 Vendor IDs updated:",
        updated_count
    )

    print(
        "Migration 009 Visits still unmatched:",
        unmatched_count
    )
# --------------------------------------------------
# Migration 010: Vehicle Baseline Preference
# --------------------------------------------------

def migration_010_vehicle_baseline_preference(
    connection
):
    """
    Add a vehicle-level preference controlling whether
    Maintenance Due may use estimated baselines when
    no exact completed service record is available.

    True:
        Use Vehicle Baseline or Odometer Baseline.

    False:
        Use completed service records only.
        Missing service history becomes History Needed.
    """

    if not table_exists(
        "vehicles"
    ):

        raise RuntimeError(
            "Migration 010 requires the "
            "vehicles table."
        )

    add_column_if_missing(
        connection,
        "vehicles",
        "use_maintenance_baseline",
        "BOOLEAN NOT NULL DEFAULT 1"
    )
# --------------------------------------------------
# Migration 011: Maintenance Setup Mode
# --------------------------------------------------

def migration_011_maintenance_setup_mode(
    connection
):
    """
    Add the Maintenance Schedule setup mode selected
    for each vehicle.

    Supported values:

    new_vehicle:
        Use the vehicle's in-service date and starting
        mileage as the initial maintenance baseline.

    purchase_reset:
        Treat the acquisition date and mileage as a
        maintenance reset point.

    as_is:
        Use exact completed service history first.
        Use odometer fallback for mileage-based items
        when exact history is unavailable.

    A NULL value means the vehicle's Maintenance
    Schedule setup has not yet been selected.
    """

    if not table_exists(
        "vehicles"
    ):

        raise RuntimeError(
            "Migration 011 requires the "
            "vehicles table."
        )

    add_column_if_missing(
        connection,
        "vehicles",
        "maintenance_baseline_mode",
        "TEXT"
    )
    # ----------------------------------------------
    # Validate Service Group Codes
    # ----------------------------------------------

    missing_group_codes = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM service_groups
            WHERE
                domain IS NULL
                OR TRIM(domain) = ''
                OR group_code IS NULL
            """
        )
    ).scalar_one()

    if missing_group_codes > 0:

        raise RuntimeError(
            "Migration 004 cannot create the "
            "Service Group unique index because "
            f"{missing_group_codes} row(s) have a "
            "missing domain or group_code."
        )

    duplicate_group_codes = connection.execute(
        text(
            """
            SELECT
                domain,
                group_code,
                COUNT(*) AS duplicate_count
            FROM service_groups
            GROUP BY
                domain,
                group_code
            HAVING COUNT(*) > 1
            """
        )
    ).fetchall()

    if duplicate_group_codes:

        raise RuntimeError(
            "Migration 004 found duplicate "
            "Service Group codes: "
            f"{duplicate_group_codes}"
        )

    # ----------------------------------------------
    # Validate Service Item Codes
    # ----------------------------------------------

    missing_service_codes = connection.execute(
        text(
            """
            SELECT COUNT(*)
            FROM service_items
            WHERE
                domain IS NULL
                OR TRIM(domain) = ''
                OR service_code IS NULL
            """
        )
    ).scalar_one()

    if missing_service_codes > 0:

        raise RuntimeError(
            "Migration 004 cannot create the "
            "Service Item unique index because "
            f"{missing_service_codes} row(s) have a "
            "missing domain or service_code."
        )

    duplicate_service_codes = connection.execute(
        text(
            """
            SELECT
                domain,
                service_code,
                COUNT(*) AS duplicate_count
            FROM service_items
            GROUP BY
                domain,
                service_code
            HAVING COUNT(*) > 1
            """
        )
    ).fetchall()

    if duplicate_service_codes:

        raise RuntimeError(
            "Migration 004 found duplicate "
            "Service Item codes: "
            f"{duplicate_service_codes}"
        )

    # ----------------------------------------------
    # Create Unique Service Group Index
    # ----------------------------------------------

    connection.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
                ux_service_groups_domain_group_code
            ON service_groups (
                domain,
                group_code
            )
            """
        )
    )

    print(
        "Migration 004 created unique index: "
        "service_groups(domain, group_code)"
    )

    # ----------------------------------------------
    # Create Unique Service Item Index
    # ----------------------------------------------

    connection.execute(
        text(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS
                ux_service_items_domain_service_code
            ON service_items (
                domain,
                service_code
            )
            """
        )
    )

    print(
        "Migration 004 created unique index: "
        "service_items(domain, service_code)"
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
    },
    {
        "id": "003",
        "name": "populate_service_catalog_fields",
        "function": migration_003_populate_service_catalog_fields
    },
    {
        "id": "004",
        "name": "unique_service_catalog_codes",
        "function": migration_004_unique_service_catalog_codes
    },
    {
        "id": "005",
        "name": "vehicle_acquisition_baseline",
        "function": migration_005_vehicle_acquisition_baseline
    },
    {
        "id": "006",
        "name": "vehicle_purchase_and_sale_prices",
        "function": migration_006_vehicle_purchase_and_sale_prices
    },
    {
        "id": "007",
        "name": "vendor_details",
        "function": migration_007_vendor_details
    },
    {
        "id": "008",
        "name": "maintenance_visit_vendor_id",
        "function": migration_008_maintenance_visit_vendor_id
    },
        {
        "id": "009",
        "name": "backfill_maintenance_visit_vendor_ids",
        "function": migration_009_backfill_maintenance_visit_vendor_ids
    },
        {
        "id": "010",
        "name": "vehicle_baseline_preference",
        "function": migration_010_vehicle_baseline_preference
    },
        {
        "id": "011",
        "name": "maintenance_setup_mode",
        "function": migration_011_maintenance_setup_mode
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