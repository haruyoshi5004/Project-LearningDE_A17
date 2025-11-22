from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from logging import getLogger

from pathlib import Path

ROUTERBASE = ""

loggerUvicorn = getLogger("uvicorn.debug")

routerPages = APIRouter()
templates = Jinja2Templates(directory=Path("src/HTMLtemplates"))

@routerPages.get(f"{ROUTERBASE}/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.jinja", {"request": request})


@routerPages.get(f"{ROUTERBASE}/forTest", response_class=HTMLResponse)
async def forTest(request: Request):
    filename = "part1.jinja"
    # return templates.TemplateResponse("test.jinja", {"request": request})
    return templates.TemplateResponse(
        "test.jinja", context={"request": request, "part": filename, "test": "hoge"}
    )


class TestObject(object):
    firstName: str
    lastName: str
    age: int

    def __init__(self, firstName: str, lastName: str, age: int) -> None:
        self.firstName = firstName
        self.lastName = lastName
        self.age = age

    def getFullName(self) -> str:
        return self.firstName + self.lastName

    def getAge(self) -> int:
        return self.age


@routerPages.get(f"{ROUTERBASE}/objectTest", response_class=HTMLResponse)
async def objectTest(request: Request):
    baseJinja = "baseTest.jinja"
    targetJinja = "objectTest.jinja"
    testObjects: list[TestObject] = [
        TestObject("gonbe", "nanashi", 15),
        TestObject("john", "doe", 20),
        TestObject("mon", "dozae", 25),
    ]
    return templates.TemplateResponse(
        baseJinja,
        context={
            "request": request,
            "content": targetJinja,
            "testObjects": testObjects,
        },
    )


# @routerPages.get("URL/to/ThisPage") == http://92.203.145.71/URL/to/ThisPage
