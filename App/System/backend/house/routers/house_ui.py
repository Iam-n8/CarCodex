from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse

from shared.template_loader import templates
from house.services.address_lookup_service import AddressLookupService
from house.services.data_export_service import HouseDataExportService

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
    return templates.TemplateResponse(
        request=request,
        name="house_ui.html",
        context={
            "request": request,
            "houses": HOUSE_LIST,
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
def house_detail_page(request: Request, house_id: int):
    house = get_house_or_none(house_id)
    if house is None:
        return RedirectResponse(url="/house-ui", status_code=303)

    return templates.TemplateResponse(
        request=request,
        name="house_detail.html",
        context={
            "request": request,
            "house": house,
        },
    )


@router.get("/house/{house_id}/edit", response_class=HTMLResponse)
def house_edit_page(request: Request, house_id: int):
    house = get_house_or_none(house_id)
    if house is None:
        return RedirectResponse(url="/house-ui", status_code=303)

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
    address: str = Form(""),
    city: str = Form(""),
    county: str = Form(""),
    state: str = Form(""),
    zip_code: str = Form(""),
    property_type: str = Form(""),
    bedrooms: int | None = Form(None),
    bathrooms: int | None = Form(None),
):
    cleaned_address = address.strip() or "Address Unknown"
    cleaned_city = city.strip() or "City Unknown"
    cleaned_county = county.strip() or "County Unknown"
    cleaned_state = state.strip() or "ST"
    cleaned_zip = zip_code.strip() or "00000"
    cleaned_type = property_type.strip() or "House"

    house = {
        "id": len(HOUSE_LIST) + 1,
        "address": cleaned_address,
        "city": cleaned_city,
        "county": cleaned_county,
        "state": cleaned_state,
        "zip_code": cleaned_zip,
        "property_type": cleaned_type,
        "bedrooms": bedrooms,
        "bathrooms": bathrooms,
    }

    # Run property lookup and save data
    lookup_result = address_service.lookup_address({
        "street": cleaned_address,
        "city": cleaned_city,
        "state": cleaned_state,
        "zip_code": cleaned_zip,
    })

    # Save lookup data to JSON and CSV
    data_export_service.save_lookup_data(house, lookup_result)
    
    # Save house info to text file
    data_export_service.save_house_info(house)

    HOUSE_LIST.append(house)

    return RedirectResponse(
        url="/house-ui",
        status_code=303,
    )


@router.post("/house/{house_id}/delete")
def house_delete_submit(house_id: int):
    for index, house in enumerate(HOUSE_LIST):
        if house["id"] == house_id:
            del HOUSE_LIST[index]
            break

    return RedirectResponse(
        url="/house-ui",
        status_code=303,
    )


@router.post("/house/{house_id}/edit")
def house_edit_submit(
    house_id: int,
    address: str = Form(""),
    city: str = Form(""),
    county: str = Form(""),
    state: str = Form(""),
    zip_code: str = Form(""),
    property_type: str = Form(""),
    bedrooms: int | None = Form(None),
    bathrooms: int | None = Form(None),
):
    house = get_house_or_none(house_id)
    if house is None:
        return RedirectResponse(url="/house-ui", status_code=303)

    house["address"] = address.strip() or house.get("address", "Address Unknown")
    house["city"] = city.strip() or house.get("city", "City Unknown")
    house["county"] = county.strip() or house.get("county", "County Unknown")
    house["state"] = state.strip() or house.get("state", "ST")
    house["zip_code"] = zip_code.strip() or house.get("zip_code", "00000")
    house["property_type"] = property_type.strip() or house.get("property_type", "House")
    house["bedrooms"] = bedrooms if bedrooms is not None else house.get("bedrooms")
    house["bathrooms"] = bathrooms if bathrooms is not None else house.get("bathrooms")

    return RedirectResponse(
        url=f"/house/{house_id}",
        status_code=303,
    )
