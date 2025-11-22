from logging import getLogger
from logging.config import dictConfig
from logging.handlers import RotatingFileHandler
from pathlib import Path
from yaml import load as loadYaml, FullLoader
import socket
import requests

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from uvicorn import run as uvicornrun

from routerUser import routerUser, routerPublic
from routerPages import routerPages


ASSETSDIR = Path("src/assets/")
PORT = 8080


def getIPs() -> dict[str, str]:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    localIP = s.getsockname()[0]
    s.close()
    globalIP = requests.get("https://ifconfig.me").text
    return {"local": localIP, "global": globalIP}


app = FastAPI()
# app.include_router(router1)
# app.include_router(routerTemplateTest)
app.include_router(routerUser)
app.include_router(routerPublic)
app.include_router(routerPages)
app.mount("/js", StaticFiles(directory=ASSETSDIR.joinpath("js/")), name="js")
app.mount("/image", StaticFiles(directory=ASSETSDIR.joinpath("image/")), name="image")
app.mount("/css", StaticFiles(directory=ASSETSDIR.joinpath("css/")), name="css")

if __name__ == "__main__":
    with open(Path("configs/log_conf.yaml"), "r", encoding="UTF-8") as configFile:
        dictConfig(loadYaml(configFile.read(), FullLoader))
    for handler in getLogger().handlers:
        if isinstance(handler, RotatingFileHandler):
            handler.doRollover()
    if not Path("configs/personal.json").exists():
        if input("first time running this project? do you wish to run setup? y/N ") == "y":
            import setup
            setup.main()
        else:
            print("you may encounter error")
    ips = getIPs()
    print(f"local IP: http://{ips["local"]}:{PORT}")
    print(f"global IP: http://{ips["global"]}:{PORT}")
    uvicornrun(
        "main:app",
        reload=True,
        host="0.0.0.0",
        port=PORT,
        log_config="configs/log_conf.yaml",
    )
