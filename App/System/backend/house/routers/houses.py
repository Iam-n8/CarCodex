# house/routers/houses.py
# ==================================================
# House API
#
# Database-backed House endpoints.
#
# Purpose:
# - List Houses
# - Create Houses
#
# Future:
# - Update House
# - Archive House
# - Restore House
# ==================================================

from fastapi import APIRouter

from database import SessionLocal

from house.models.house_model import House

from helpers.crud_helpers import delete_record


router = APIRouter()


# ==================================================
# Get Active Houses
# ==================================================

@router.get("/houses")
def get_houses():

    db = SessionLocal()

    houses = db.query(
        House
    ).filter(
        House.archived == False
    ).all()

    results = []

    for house in houses:

        results.append({
            "id": house.id,
            "name": house.name,
            "parcel_id": house.parcel_id,
            "address": house.address,
            "city": house.city,
            "county": house.county,
            "state": house.state,
            "zip_code": house.zip_code,
            "date_acquired": house.date_acquired,
            "purchase_price_cents": house.purchase_price_cents
        })

    db.close()

    return results
# ==================================================
# Delete House
# ==================================================

@router.delete("/houses/{house_id}")
def delete_house(
    house_id: int
):

    db = SessionLocal()

    result = delete_record(
        db=db,
        model_class=House,
        record_id=house_id,
        record_name="House"
    )

    db.close()

    return result


