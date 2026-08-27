# --------------------------------------------------
# app_paths.py
#
# Central path helper for Maintain Hub
#
# Purpose:
# - Keep Maintain Hub portable
# - Avoid hardcoded drive letters
# - Separate application files from customer data
# - Support running from a jump drive
#
# Folder Layout
#
# MaintainHub
# │
# ├── App
# │   ├── .venv
# │   ├── alembic
# │   └── System
# │
# └── YourDataFolder
#     │
#     ├── App Data
#     │   ├── Backups
#     │   ├── Configuration
#     │   └── Database
#     │
#     ├── Boats
#     ├── House
#     ├── Reports
#     └── Vehicles
#
# Notes:
# - App contains application code only.
# - YourDataFolder contains customer data only.
# - Vehicle folders remain easy to browse.
# - Database files are isolated from vehicle files.
# - Backups, configuration, and reports are grouped
#   under App Data.
# --------------------------------------------------

from pathlib import Path


# --------------------------------------------------
# Application Root Folders
# --------------------------------------------------

def get_backend_root() -> Path:
    """
    MaintainHub/App/System/backend
    """
    return Path(__file__).resolve().parents[1]


def get_system_root() -> Path:
    """
    MaintainHub/App/System
    """
    return Path(__file__).resolve().parents[2]


def get_app_root() -> Path:
    """
    MaintainHub/App
    """
    return Path(__file__).resolve().parents[3]


def get_maintain_hub_root() -> Path:
    """
    MaintainHub
    """
    return Path(__file__).resolve().parents[4]


# --------------------------------------------------
# Customer Data Root
# --------------------------------------------------

def get_customer_data_folder() -> Path:
    """
    MaintainHub/YourDataFolder
    """
    return (
        get_maintain_hub_root()
        / "YourDataFolder"
    )


# --------------------------------------------------
# App Data
# --------------------------------------------------

def get_app_data_folder() -> Path:
    """
    MaintainHub/YourDataFolder/App Data
    """
    return (
        get_customer_data_folder()
        / "App Data"
    )


def get_database_folder() -> Path:
    """
    MaintainHub/YourDataFolder/App Data/Database
    """
    return (
        get_app_data_folder()
        / "Database"
    )


def get_database_path() -> Path:
    """
    MaintainHub/YourDataFolder/App Data/Database/maintainhub.db
    """
    return (
        get_database_folder()
        / "maintainhub.db"
    )


def get_configuration_folder() -> Path:
    """
    MaintainHub/YourDataFolder/App Data/Configuration
    """
    return (
        get_app_data_folder()
        / "Configuration"
    )


def get_service_catalog_csv_path() -> Path:
    """
    MaintainHub/YourDataFolder/App Data/Configuration/ServiceCatalog.csv
    """
    return (
        get_configuration_folder()
        / "ServiceCatalog.csv"
    )


def get_backups_folder() -> Path:
    """
    MaintainHub/YourDataFolder/App Data/Backups
    """
    return (
        get_app_data_folder()
        / "Backups"
    )


# --------------------------------------------------
# Vehicle Data
# --------------------------------------------------

def get_vehicle_data_folder() -> Path:
    """
    MaintainHub/YourDataFolder/Vehicles
    """
    return (
        get_customer_data_folder()
        / "Vehicles"
    )


# --------------------------------------------------
# Future Domains
# --------------------------------------------------

def get_house_data_folder() -> Path:
    """
    MaintainHub/YourDataFolder/House
    """
    return (
        get_customer_data_folder()
        / "House"
    )


def get_boat_data_folder() -> Path:
    """
    MaintainHub/YourDataFolder/Boats
    """
    return (
        get_customer_data_folder()
        / "Boats"
    )


def get_reports_folder() -> Path:
    """
    MaintainHub/YourDataFolder/Reports
    """
    return (
        get_customer_data_folder()
        / "Reports"
    )


# --------------------------------------------------
# Create Customer Data Structure
# --------------------------------------------------

def ensure_customer_data_folders() -> None:
    """
    Create the Maintain Hub customer-data folder structure.
    """

    folders = [
        get_customer_data_folder(),

        get_app_data_folder(),
        get_database_folder(),
        get_configuration_folder(),
        get_backups_folder(),

        get_vehicle_data_folder(),
        get_house_data_folder(),
        get_boat_data_folder(),
        get_reports_folder(),
    ]

    for folder in folders:
        folder.mkdir(
            parents=True,
            exist_ok=True
        )