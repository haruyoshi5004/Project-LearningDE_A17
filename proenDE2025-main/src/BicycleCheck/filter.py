from ultralytics import YOLO

from logging import getLogger

loggerBC = getLogger("BicycleCheck.debug")

def hoge() -> str:
    loggerBC.info("hogehoge?")
    return "test"

if __name__=="__main__":
    from logging.config import dictConfig
    from yaml import FullLoader, load as loadYaml

    with open("configs/log_conf.yaml", "r") as configFile:
        dictConfig(loadYaml(configFile.read(), FullLoader))
    hoge()
