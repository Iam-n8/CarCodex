# models.py


from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from database import Base


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)

    nickname = Column(String)
    vin = Column(String)

    year = Column(Integer)

    make = Column(String)
    model = Column(String)
    trim = Column(String)

    current_mileage = Column(Integer)


class MileageHistory(Base):
    __tablename__ = "mileage_history"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    mileage = Column(Integer)

    entry_date = Column(String)


class ServiceRecord(Base):
    __tablename__ = "service_records"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))


    maintenance_visit_id = Column(
        Integer,
        nullable=True
    )

    service_status = Column(
        String,
        default="COMPLETED"
    )



    service_type = Column(String)

    service_date = Column(String)

    mileage = Column(Integer)

    provider = Column(String)

    cost = Column(Integer)

    notes = Column(String)

    next_service_mileage = Column(Integer)

    next_service_date = Column(String)
    

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

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    service_type = Column(String)

    interval_miles = Column(Integer)

    interval_months = Column(Integer)

    estimated_cost = Column(Float)

    uses_health_indicator = Column(String)

    notes = Column(String)
class MaintenanceVisit(Base):
    __tablename__ = "maintenance_visits"

    id = Column(Integer, primary_key=True, index=True)

    vehicle_id = Column(Integer, ForeignKey("vehicles.id"))

    visit_date = Column(String)

    mileage = Column(Integer)

    vendor = Column(String)

    invoice_number = Column(String)

    total_cost = Column(Float)

    notes = Column(String)

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
