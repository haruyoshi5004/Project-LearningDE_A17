from fastapi import APIRouter, status as httpStatus
from fastapi.responses import RedirectResponse

from logging import getLogger

from BicycleCheck import filter

ROUTERBASE = ""

loggerUvicorn = getLogger(f"uvicorn.debug")

router1 = APIRouter()


@router1.get(f"{ROUTERBASE}/")
async def root() -> dict[str, str]:
    loggerUvicorn.info("test test test")
    return {"message": "hello world!"}


@router1.get(f"{ROUTERBASE}/test")
async def test() -> str:
    return filter.hoge()


@router1.get(f"{ROUTERBASE}/redirect")
async def redirector() -> RedirectResponse:
    return RedirectResponse("/test", status_code=httpStatus.HTTP_303_SEE_OTHER)
