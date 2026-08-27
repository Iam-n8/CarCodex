from fastapi import APIRouter
from schemas.cost import OwnershipCostCreate 

from database import SessionLocal
from models import OwnershipCost

router = APIRouter()


@router.get("/ownership-costs")
def get_ownership_costs():

    db = SessionLocal()

    costs = db.query(OwnershipCost).all()

    results = []

    for cost in costs:
        results.append({
            "id": cost.id,
            "vehicle_id": cost.vehicle_id,
            "category": cost.category,
            "description": cost.description,
            "amount": cost.amount
        })

    db.close()

    return results


@router.post("/ownership-costs")
def create_ownership_cost(cost: OwnershipCostCreate):

    db = SessionLocal()

    new_cost = OwnershipCost(
        vehicle_id=cost.vehicle_id,
        cost_date=cost.cost_date,
        category=cost.category,
        description=cost.description,
        vendor=cost.vendor,
        amount=cost.amount,
        mileage=cost.mileage
    )

    db.add(new_cost)
    db.commit()
    db.refresh(new_cost)

    db.close()

    return {
        "message": "Ownership cost added",
        "id": new_cost.id
    }
