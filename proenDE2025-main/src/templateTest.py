from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from logging import getLogger

from pathlib import Path

ROUTERBASE = ""

loggerUvicorn = getLogger("uvicorn.debug")

routerTemplateTest = APIRouter()
templates = Jinja2Templates(directory=Path("src/HTMLtemplates"))


class TestClass(object):
    number: int

    def __init__(self, number: int) -> None:
        self.number = number


@routerTemplateTest.get(f"{ROUTERBASE}/templateTest", response_class=HTMLResponse)
async def read_root(request: Request):
    testInstance = TestClass(20)
    testList = ["apple", "orange", "peach"]
    return templates.TemplateResponse(
        "test1.jinja",
        {
            "request": request,
            "message": "testtest",
            "testObject": testInstance,
            "fruitNames": testList,
        },
    )
