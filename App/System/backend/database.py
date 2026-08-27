# --------------------------------------------------
# database.py
#
# Maintain Hub Database Configuration
#
# Purpose:
# - Create the SQLAlchemy database engine
# - Provide database sessions
# - Define the application's base model class
# - Centralize database path management
#
# Notes:
# - Database location is controlled by
#   helpers.app_paths.get_database_path()
#
# - The database should be stored in:
#
#   MaintainHub/
#   └── YourDataFolder/
#       └── App Data/
#           └── Database/
#               └── maintainhub.db
#
# - Avoid hardcoded database paths.
#
# - This design keeps application files
#   separate from customer data and
#   supports portable installations.
#
# - Future database migrations should
#   continue using this centralized path.
# --------------------------------------------------

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

from helpers.app_paths import get_database_path


# --------------------------------------------------
# Database Path
# --------------------------------------------------

DATABASE_PATH = get_database_path()

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# --------------------------------------------------
# SQLAlchemy Engine
# --------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# --------------------------------------------------
# Session Factory
# --------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# --------------------------------------------------
# Base Model Class
# --------------------------------------------------

Base = declarative_base()


# --------------------------------------------------
# Developer Notes
# --------------------------------------------------
#
# Current Database Location:
#
#   MaintainHub/
#   └── YourDataFolder/
#       └── App Data/
#           └── Database/
#               └── maintainhub.db
#
# Related Paths:
#
#   Vehicle Data
#   └── YourDataFolder/Vehicles
#
#   Configuration
#   └── YourDataFolder/App Data/Configuration
#
#   Reports
#   └── YourDataFolder/Reports
#
#   Backups
#   └── YourDataFolder/App Data/Backups
#
# All storage locations should be obtained
# through helpers.app_paths and should not
# be hardcoded elsewhere in the application.
# --------------------------------------------------