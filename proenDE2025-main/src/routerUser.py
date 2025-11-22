from typing import Optional

from logging import getLogger

from fastapi import APIRouter, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

from schemas import User, Bicycle, BicycleDetect, Area, Car, UserSql, AccessToken


ROUTERBASE = "/api"
ROUTERBASEUSER = ROUTERBASE + "/users"

routerUser = APIRouter()
routerPublic = APIRouter()


@routerUser.post(
    f"{ROUTERBASEUSER}/login",
    response_class=JSONResponse,
    description="get token from email and password",
)
async def login(token: AccessToken = Depends(User.login)):
    # return JSONResponse(content=token.model_dump(), status_code=status.HTTP_200_OK)
    return token


@routerUser.get(f"{ROUTERBASEUSER}/me", response_class=JSONResponse)
async def checkUser(user: User | None = Depends(User.require)):
    print(type(user))
    if user is None:
        return JSONResponse({"username": None}, status_code=status.HTTP_404_NOT_FOUND)
    else:
        return JSONResponse(user.model_dump(), status_code=status.HTTP_200_OK)


@routerPublic.get(f"{ROUTERBASE}/bicycle", response_class=JSONResponse)
async def getBicycle(bicycle: Bicycle | None = Depends(Bicycle.getOne)):
    if bicycle is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
        )
    return JSONResponse(bicycle.model_dump(), status_code=status.HTTP_200_OK)


@routerPublic.get(f"{ROUTERBASE}/bicycledetect", response_class=JSONResponse)
async def getBicyclesdetect(
    bicycledetect: BicycleDetect | None = Depends(BicycleDetect.getOne),
):
    return JSONResponse(bicycledetect, status_code=status.HTTP_200_OK)


@routerPublic.get(f"{ROUTERBASE}/area", response_class=JSONResponse)
async def getArea(area: Area | None = Depends(Area.getOne)):
    return JSONResponse(area, status_code=status.HTTP_200_OK)


@routerPublic.get(f"{ROUTERBASE}/car", response_class=JSONResponse)
async def getCar(car: Car | None = Depends(Car.getOne)):
    return JSONResponse(car, status_code=status.HTTP_200_OK)
