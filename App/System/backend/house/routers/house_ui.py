# App/System/backend/house/routers/house_ui.py

from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from shared.template_loader import templates
from house.services.address_lookup_service import AddressLookupService
from house.services.data_export_service import HouseDataExportService

from database import SessionLocal
from house.models.house_model import House


router = APIRouter()
address_service = AddressLookupService()
data_export_service = HouseDataExportService()

HOUSE_LIST = []


def get_house_or_none(house_id: int):
    for house in HOUSE_LIST:
        if house["id"] == house_id:
            return house
    return None


@router.get("/house-ui", response_class=HTMLResponse)
def house_ui(request: Request):

    db = SessionLocal()

    houses = db.query(
        House
    ).filter(
        House.archived == False
    ).all()

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="house_ui.html",
        context={
            "request": request,
            "houses": houses,
        },
    )


@router.post("/house/lookup")
def house_lookup(address: str = Form(""), city: str = Form(""), state: str = Form(""), zip_code: str = Form("")):
    """Lookup property details from Sarasota County ArcGIS API."""
    result = address_service.lookup_address({
        "street": address,
        "city": city,
        "state": state,
        "zip_code": zip_code,
    })
    return JSONResponse(content=result)


@router.get("/house/{house_id}", response_class=HTMLResponse)
def house_detail_page(
    request: Request,
    house_id: int
):

    db = SessionLocal()

    house = db.query(
        House
    ).filter(
        House.id == house_id,
        House.archived == False
    ).first()

    db.close()

    if house is None:

        return RedirectResponse(
            url="/house-ui",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="house_detail.html",
        context={
            "request": request,
            "house": house,
        },
    )

@router.get("/house/{house_id}/edit", response_class=HTMLResponse)
def house_edit_page(
    request: Request,
    house_id: int
):

    db = SessionLocal()

    house = db.query(
        House
    ).filter(
        House.id == house_id,
        House.archived == False
    ).first()

    db.close()

    if house is None:

        return RedirectResponse(
            url="/house-ui",
            status_code=303
        )

    return templates.TemplateResponse(
        request=request,
        name="house_edit.html",
        context={
            "request": request,
            "house": house,
        },
    )


@router.get("/house-add", response_class=HTMLResponse)
def house_add_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="house_add.html",
        context={"request": request},
    )


@router.post("/house-add")
def house_add_submit(
    name: str = Form(""),
    parcel_id: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    county: str = Form(""),
    state: str = Form(""),
    zip_code: str = Form("")
):
    cleaned_name = name.strip() or cleaned_address
    cleaned_parcel_id = parcel_id.strip()
    cleaned_address = address.strip() or "Address Unknown"
    cleaned_city = city.strip() or "City Unknown"
    cleaned_county = county.strip() or "County Unknown"
    cleaned_state = state.strip() or "ST"
    cleaned_zip = zip_code.strip() or "00000"

    db = SessionLocal()

    house = House(
        name=cleaned_name,
        parcel_id=cleaned_parcel_id,
        address=cleaned_address,
        city=cleaned_city,
        county=cleaned_county,
        state=cleaned_state,
        zip_code=cleaned_zip
    )

    db.add(house)

    db.commit()

    db.refresh(house)

    db.close()

    # Run property lookup and save data
    lookup_result = address_service.lookup_address({
        "street": cleaned_address,
        "city": cleaned_city,
        "state": cleaned_state,
        "zip_code": cleaned_zip,
    })
    house_data = {
        "id": house.id,
        "name": house.name,
        "parcel_id": house.parcel_id,
        "address": house.address,
        "city": house.city,
        "county": house.county,
        "state": house.state,
        "zip_code": house.zip_code
    }    

    data_export_service.save_lookup_data(
        house_data,
        lookup_result
    )

    data_export_service.save_house_info(
        house_data
    )

    return RedirectResponse(
        url="/house-ui",
        status_code=303,
    )


@router.post("/house/{house_id}/delete")
def house_delete_submit(
    house_id: int
):

    db = SessionLocal()

    house = db.query(
        House
    ).filter(
        House.id == house_id
    ).first()

    if house:

        db.delete(
            house
        )

        db.commit()

    db.close()

    return RedirectResponse(
        url="/house-ui",
        status_code=303,
    )


@router.post("/house/{house_id}/edit")
def house_edit_submit(
    house_id: int,
    name: str = Form(""),
    parcel_id: str = Form(""),
    address: str = Form(""),
    city: str = Form(""),
    county: str = Form(""),
    state: str = Form(""),
    zip_code: str = Form(""),):
    db = SessionLocal()

    house = db.query(
        House
    ).filter(
        House.id == house_id,
        House.archived == False
    ).first()
    if house is None:
        return RedirectResponse(url="/house-ui", status_code=303)

    house["name"] = name.strip() or house.get("name", "Property")
    house["parcel_id"] = parcel_id.strip() or house.get("parcel_id", "")
    house["address"] = address.strip() or house.get("address", "Address Unknown")
    house["city"] = city.strip() or house.get("city", "City Unknown")
    house["county"] = county.strip() or house.get("county", "County Unknown")
    house["state"] = state.strip() or house.get("state", "ST")
    house["zip_code"] = zip_code.strip() or house.get("zip_code", "00000")

    return RedirectResponse(
        url=f"/house/{house_id}",
        status_code=303,
    )
