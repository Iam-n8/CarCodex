# --------------------------------------------------
# app_paths.py
#
# Central path helper for CarCodex
#
# Purpose:
# - Keep CarCodex portable
# - Avoid hardcoded drive letters
# - Support running from a jump drive
# --------------------------------------------------

from pathlib import Path


# --------------------------------------------------
# Root Folders
# --------------------------------------------------

def get_backend_root() -> Path:
    """
    Return:
    CarCodex/System/backend
    """

    return Path(
        __file__
    ).resolve().parents[1]


def get_system_root() -> Path:
    """
    Return:
    CarCodex/System
    """

    return Path(
        __file__
    ).resolve().parents[2]


def get_system_data_folder() -> Path:
    """
    Return:
    CarCodex/System/Data
    """

    return (
        get_system_root()
        / "Data"
    )


def get_backend_data_folder() -> Path:
    """
    Return:
    CarCodex/System/backend/CarCodex_Data
    """

    return (
        get_backend_root()
        / "CarCodex_Data"
    )


def get_vehicle_data_folder() -> Path:
    """
    Return:
    CarCodex/System/backend/CarCodex_Data/Vehicles
    """

    return (
        get_backend_data_folder()
        / "Vehicles"
    )


def get_service_catalog_csv_path() -> Path:
    """
    Return:
    CarCodex/System/Data/ServiceCatalog.csv
    """

    return (
        get_system_data_folder()
        / "ServiceCatalog.csv"
    )
