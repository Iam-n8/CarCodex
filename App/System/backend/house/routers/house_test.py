from fastapi import APIRouter, Form
from fastapi.responses import HTMLResponse

from shared.template_loader import templates
from schemas.house import HouseAddressLookup
from house.services.address_lookup_service import AddressLookupService

router = APIRouter(tags=["house"])
service = AddressLookupService()


@router.get("/house-ui", response_class=HTMLResponse)
@router.get("/house/ui", response_class=HTMLResponse)
def house_lookup_test_page(request):
    return templates.TemplateResponse(
        request=request,
        name="house_address_lookup_test.html",
        context={"request": request}
    )


@router.get("/house/test", response_class=HTMLResponse)
def house_lookup_test_page_alt(request):
    return templates.TemplateResponse(
        request=request,
        name="house_address_lookup_test.html",
        context={"request": request}
    )


@router.post("/house/lookup")
def house_lookup(payload: HouseAddressLookup):
    result = service.lookup_address(payload.model_dump())
    return result


@router.post("/house/lookup-form")
def house_lookup_form(
    street: str = Form(...),
    city: str = Form(...),
    state: str = Form(...),
    zip_code: str = Form(...),
):
    payload = {
        "street": street,
        "city": city,
        "state": state,
        "zip_code": zip_code,
        "country": "US",
    }
    return service.lookup_address(payload)
