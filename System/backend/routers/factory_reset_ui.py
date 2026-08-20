# --------------------------------------------------
# factory_reset_ui.py
#
# Factory Reset UI Routes
#
# Purpose:
# - Show Factory Reset confirmation page
# - Run full reset through helpers/factory_reset.py
# - Keep reset workflow separate from other routers
# --------------------------------------------------

from fastapi import (
    APIRouter,
    Request
)

from fastapi.responses import (
    HTMLResponse,
    RedirectResponse
)

from fastapi.templating import (
    Jinja2Templates
)

from helpers.factory_reset import (
    run_factory_reset
)


router = APIRouter()

templates = Jinja2Templates(
    directory="templates"
)


# --------------------------------------------------
# Factory Reset Page
# --------------------------------------------------

@router.get(
    "/factory-reset",
    response_class=HTMLResponse
)
def factory_reset_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="factory_reset.html",
        context={
            "request": request
        }
    )


# --------------------------------------------------
# Factory Reset Submit
# --------------------------------------------------

@router.post(
    "/factory-reset"
)
def factory_reset_submit():

    result = run_factory_reset()

    print(
        "FACTORY RESET RESULT:",
        result
    )

    return RedirectResponse(
        url="/vehicles-ui",
        status_code=303
    )
