# models.py


from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from database import Base


class Vehicle(Base):

    __tablename__ = "vehicles"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    nickname = Column(
        String
    )

    vin = Column(
        String
    )

    year = Column(
        Integer
    )

    make = Column(
        String
    )

    model = Column(
        String
    )

    trim = Column(
        String
    )

    current_mileage = Column(
        Integer
    )

    date_acquired = Column(
        String,
        nullable=True
    )

    mileage_at_acquisition = Column(
        Integer,
        nullable=True
    )

    vehicle_condition = Column(
        String,
        nullable=True
    )
    purchase_price_cents = Column(
        Integer,
        nullable=True
    )

    sold_price_cents = Column(
        Integer,
        nullable=True
    )    

    archived = Column(
        Boolean,
        default=False
    )

class MileageHistory(Base):
    __tablename__ = "mileage_history"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    mileage = Column(Integer)

    entry_date = Column(String)



# ==================================================
# Service Record
#
# Stores the work performed during a Maintenance Visit.
#
# Example:
#
# Primary Reason:
#     Oil Change
#
# Parts Used:
#     Mobil1 5W-30
#     ACDelco PF64 Filter
#
# Additional Services:
#     Tire Rotation
#     Multi-Point Inspection
#
# Notes:
#     Customer requested tire pressure check.
# ==================================================

class ServiceRecord(Base):

    __tablename__ = "service_records"

    # ----------------------------------------------
    # Primary Key
    # ----------------------------------------------

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ----------------------------------------------
    # Vehicle Reference
    # ----------------------------------------------

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id")
    )

    # ----------------------------------------------
    # Maintenance Visit Reference
    # ----------------------------------------------

    maintenance_visit_id = Column(
        Integer,
        nullable=True
    )

    # ----------------------------------------------
    # Primary Reason For Service
    #
    # Examples:
    #   Oil Change
    #   Brake Service
    #   Tire Service
    #   Transmission Service
    #   Warranty Repair
    # ----------------------------------------------

    primary_reason = Column(
        String
    )

    # ----------------------------------------------
    # Parts Used
    #
    # Multiline field.
    #
    # Example:
    #
    # Mobil1 5W-30
    # PF64 Oil Filter
    # ----------------------------------------------

    parts_used = Column(
        String
    )

    # ----------------------------------------------
    # Additional Services
    #
    # Stored as text for now.
    #
    # Example:
    #
    # Tire Rotation
    # Multi-Point Inspection
    # Cabin Air Filter
    # ----------------------------------------------

    additional_services = Column(
        String
    )

    # ----------------------------------------------
    # Status
    #
    # COMPLETED
    # RECOMMENDED
    # DECLINED
    # ----------------------------------------------

    service_status = Column(
        String,
        default="COMPLETED"
    )
    archived = Column(
        Boolean,
        default=False
    )

    # ----------------------------------------------
    # Original Service Type
    #
    # Keep temporarily for backward compatibility.
    #
    # Can be removed later after migration.
    # ----------------------------------------------

    service_type = Column(
        String
    )

    # ----------------------------------------------
    # Service Date
    # ----------------------------------------------

    service_date = Column(
        String
    )

    # ----------------------------------------------
    # Vehicle Mileage
    # ----------------------------------------------

    mileage = Column(
        Integer
    )

    # ----------------------------------------------
    # Service Provider
    # ----------------------------------------------

    provider = Column(
        String
    )

    # ----------------------------------------------
    # Cost
    # ----------------------------------------------

    cost = Column(
        Integer
    )

    # ----------------------------------------------
    # Notes
    #
    # Technician notes
    # Customer notes
    # Follow-up notes
    # ----------------------------------------------

    notes = Column(
        String
    )

    # ----------------------------------------------
    # Future Service Tracking
    # ----------------------------------------------

    next_service_mileage = Column(
        Integer
    )

    next_service_date = Column(
        String
    )
class ServiceType(Base):

    __tablename__ = "service_types"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(String)

    archived = Column(
        Boolean,
        default=False
    )
# ==================================================
# Service Group
#
# Organizes service items into logical groups.
#
# Examples:
# Engine
# Tires
# Transmission
# Brakes
# ==================================================

class ServiceGroup(Base):

    __tablename__ = "service_groups"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    domain = Column(
        String
    )

    group_code = Column(
        Integer
    )

    name = Column(
        String
    )

    display_order = Column(
        Integer,
        default=0
    )

    inactive = Column(
        Boolean,
        default=False
    )

    notes = Column(
        String
    )

# ==================================================
# Service Item
#
# Specific maintenance, repair, inspection,
# replacement, or modification inside a group.
#
# Examples:
# Engine -> Oil Change
# Transmission -> DCT Transmission Canister Filter
# Body -> Windshield Replacement
#
# Important:
# Maintenance Due matches the specific service item,
# not only the group.
# ==================================================

class ServiceItem(Base):

    __tablename__ = "service_items"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    group_id = Column(
        Integer,
        ForeignKey("service_groups.id")
    )

    domain = Column(
        String
    )

    service_code = Column(
        Integer
    )

    item_name = Column(
        String
    )

    service_type_match = Column(
        String
    )

    service_category = Column(
        String
    )

    track_for_maintenance_due = Column(
        Boolean,
        default=False
    )

    default_miles_interval = Column(
        Integer,
        nullable=True
    )

    default_period_months = Column(
        Integer,
        nullable=True
    )

    display_order = Column(
        Integer,
        default=0
    )

    inactive = Column(
        Boolean,
        default=False
    )

    notes = Column(
        String
    )  


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    event_date = Column(String)

    mileage = Column(Integer)

    category = Column(String)

    event_type = Column(String)

    description = Column(String)

    location = Column(String)

    cost = Column(Integer)

class Snapshot(Base):
    __tablename__ = "snapshots"

    id = Column(Integer, primary_key=True, index=True)

    timestamp = Column(String)

    action = Column(String)

    description = Column(String)

    vehicle_id = Column(Integer)

class OwnershipCost(Base):
    __tablename__ = "ownership_costs"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    cost_date = Column(String)

    category = Column(String)

    description = Column(String)

    vendor = Column(String)

    amount = Column(Float)

    mileage = Column(Integer)

class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    
    maintenance_visit_id = Column(
        Integer,
        nullable=True
    )

    document_type = Column(String)

    file_name = Column(String)

    file_path = Column(String)

    upload_date = Column(String)

    notes = Column(String)

    archived = Column(Boolean, default=False)

class MaintenanceSchedule(Base):
    __tablename__ = "maintenance_schedule"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id")
    )

    item_name = Column(
        String
    )

    service_type_match = Column(
        String
    )

    miles_interval = Column(
        Integer,
        nullable=True
    )

    period_months = Column(
        Integer,
        nullable=True
    )

    inactive = Column(
        Boolean,
        default=False
    )

    notes = Column(
        String
    )

    display_order = Column(
        Integer,
        default=0
    )

class MaintenanceVisit(Base):
    __tablename__ = "maintenance_visits"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    vendor_id = Column(
        Integer,
        nullable=True
    )

    visit_date = Column(String)

    mileage = Column(Integer)

    vendor = Column(String)

    invoice_number = Column(String)

    total_cost = Column(Float)

    notes = Column(String)

    archived = Column(
    Boolean,
    default=False
)

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)

    vendor_type = Column(String)

    address_1 = Column(String)
    address_2 = Column(String)

    city = Column(String)
    state = Column(String)
    zip_code = Column(String)

    phone = Column(String)
    email = Column(String)

    website = Column(String)

    primary_contact = Column(String)

    notes = Column(String)

    is_preferred = Column(Boolean, default=False)

    archived = Column(Boolean, default=False)
