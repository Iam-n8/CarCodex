# --------------------------------------------------
# service_catalog_loader.py
#
# Shared Service Catalog CSV loader
#
# Purpose:
# - Read the master ServiceCatalog.csv file
# - Support multiple future domains:
#   Vehicle, House, Pool, etc.
# - Provide one source of truth for Service Catalog
#   and MaintSch seed defaults
# --------------------------------------------------

import os
import csv


# --------------------------------------------------
# CSV Path
# --------------------------------------------------

def get_service_catalog_csv_path():
    """
    Return the ServiceCatalog.csv path.

    Expected location:
    C:\\CarCodex\\System\\Data\\ServiceCatalog.csv
    """

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "Data",
            "ServiceCatalog.csv"
        )
    )


# --------------------------------------------------
# Clean CSV Value
# --------------------------------------------------

def clean_csv_value(
    value
):
    """
    Normalize CSV text values.
    """

    if value is None:

        return ""

    return value.strip()


# --------------------------------------------------
# CSV Integer
# --------------------------------------------------

def csv_int(
    value,
    default=0
):
    """
    Convert a CSV value to int safely.
    """

    value = clean_csv_value(
        value
    )

    if not value:

        return default

    try:

        return int(
            value
        )

    except ValueError:

        return default


# --------------------------------------------------
# CSV Boolean
# --------------------------------------------------

def csv_bool(
    value
):
    """
    Convert CSV yes/no values to boolean.
    """

    value = clean_csv_value(
        value
    ).lower()

    return value in [
        "yes",
        "true",
        "1",
        "y"
    ]


# --------------------------------------------------
# Load All Service Catalog Rows
# --------------------------------------------------

def load_service_catalog_csv():
    """
    Load all rows from ServiceCatalog.csv.
    """

    csv_path = get_service_catalog_csv_path()

    rows = []

    with open(
        csv_path,
        "r",
        encoding="utf-8-sig",
        newline=""
    ) as file:

        reader = csv.DictReader(
            file
        )

        for row in reader:

            rows.append(
                row
            )

    return rows


# --------------------------------------------------
# Load Rows For Domain
# --------------------------------------------------

def load_service_catalog_rows_for_domain(
    domain_name="Vehicle"
):
    """
    Load ServiceCatalog.csv rows for one domain.

    For CarCodex v1.1, domain_name should be:
    Vehicle
    """

    rows = load_service_catalog_csv()

    domain_rows = []

    requested_domain = clean_csv_value(
        domain_name
    ).lower()

    for row in rows:

        row_domain = clean_csv_value(
            row.get(
                "domain"
            )
        ).lower()

        if row_domain == requested_domain:

            domain_rows.append(
                row
            )

    return domain_rows


# --------------------------------------------------
# Load Vehicle Service Catalog Rows
# --------------------------------------------------

def load_vehicle_service_catalog_rows():
    """
    Load only Vehicle domain rows.
    """

    return load_service_catalog_rows_for_domain(
        "Vehicle"
    )


# --------------------------------------------------
# Load Maintenance Trackable Rows
# --------------------------------------------------

def load_maintenance_trackable_rows(
    domain_name="Vehicle"
):
    """
    Load rows that should be used for MaintSch.

    Uses:
    domain = Vehicle
    track_for_maintenance_due = yes
    """

    rows = load_service_catalog_rows_for_domain(
        domain_name
    )

    trackable_rows = []

    for row in rows:

        if csv_bool(
            row.get(
                "track_for_maintenance_due"
            )
        ):

            trackable_rows.append(
                row
            )

    return trackable_rows