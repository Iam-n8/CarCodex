from sqlalchemy import Column, Integer, String, ForeignKey
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

    service_type = Column(String)

    service_date = Column(String)

    mileage = Column(Integer)

    provider = Column(String)

    cost = Column(Integer)

    notes = Column(String)

    next_service_mileage = Column(Integer)

    next_service_date = Column(String)