# template_loader.py

from fastapi.templating import Jinja2Templates

from jinja2 import (
    Environment,
    FileSystemLoader
)

template_loader = FileSystemLoader([
    "templates",

    "vehicle/templates",
    "house/templates",
    "boat/templates",
    "pet/templates",

    "shared/templates"
])

templates = Jinja2Templates(
    env=Environment(
        loader=template_loader
    )
)



'''' 
THIS GETS PLACED IN NEW ROUTERS: 

from shared.template_loader import (
2
templates
3
)

'''