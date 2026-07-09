# vendor 
# routers/vendor.py

from fastapi import APIRouter

from database import SessionLocal
from models import Vendor

from schemas.vendor import VendorCreate

router = APIRouter()


@router.get("/vendors")
def get_vendors():

    db = SessionLocal()

    vendors = db.query(Vendor).filter(
        Vendor.archived == False
    ).all()

    results = []

    for vendor in vendors:

        results.append({
            "id": vendor.id,
            "name": vendor.name,
            "vendor_type": vendor.vendor_type,
            "phone": vendor.phone,
            "is_preferred": vendor.is_preferred
        })

    db.close()

    return results


@router.post("/vendors")
def create_vendor(
    vendor: VendorCreate
):

    db = SessionLocal()

    new_vendor = Vendor(
        name=vendor.name,
        vendor_type=vendor.vendor_type,
        address_1=vendor.address_1,
        address_2=vendor.address_2,
        city=vendor.city,
        state=vendor.state,
        zip_code=vendor.zip_code,
        phone=vendor.phone,
        email=vendor.email,
        website=vendor.website,
        primary_contact=vendor.primary_contact,
        notes=vendor.notes,
        is_preferred=vendor.is_preferred
    )

    db.add(new_vendor)

    db.commit()

    db.refresh(new_vendor)

    db.close()

    return {
        "message": "Vendor added",
        "id": new_vendor.id
    }
@router.get("/vendors/{vendor_id}")
def get_vendor(
    vendor_id: int
):

    db = SessionLocal()

    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id
    ).first()

    if not vendor:

        db.close()

        return {
            "error": "Vendor not found"
        }

    result = {
        "id": vendor.id,
        "name": vendor.name,
        "vendor_type": vendor.vendor_type,

        "address_1": vendor.address_1,
        "address_2": vendor.address_2,

        "city": vendor.city,
        "state": vendor.state,
        "zip_code": vendor.zip_code,

        "phone": vendor.phone,
        "email": vendor.email,

        "website": vendor.website,

        "primary_contact": vendor.primary_contact,

        "notes": vendor.notes,

        "is_preferred": vendor.is_preferred,

        "archived": vendor.archived
    }

    db.close()

    return result
@router.put("/vendors/{vendor_id}")
def update_vendor(
    vendor_id: int,
    vendor_data: VendorCreate
):

    db = SessionLocal()

    vendor = db.query(Vendor).filter(
        Vendor.id == vendor_id
    ).first()

    if not vendor:

        db.close()

        return {
            "error": "Vendor not found"
        }

    vendor.name = vendor_data.name

    vendor.vendor_type = vendor_data.vendor_type

    vendor.address_1 = vendor_data.address_1
    vendor.address_2 = vendor_data.address_2

    vendor.city = vendor_data.city
    vendor.state = vendor_data.state
    vendor.zip_code = vendor_data.zip_code

    vendor.phone = vendor_data.phone
    vendor.email = vendor_data.email

    vendor.website = vendor_data.website

    vendor.primary_contact = vendor_data.primary_contact

    vendor.notes = vendor_data.notes

    vendor.is_preferred = vendor_data.is_preferred

    db.commit()

    db.close()

    return {
        "message": "Vendor updated"
    }