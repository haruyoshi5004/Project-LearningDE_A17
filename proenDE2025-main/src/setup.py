#!python3

from pathlib import Path
from os import PathLike, mkdir
from shutil import rmtree
import json
import typing


def createDir(path: typing.Union[str, PathLike]) -> None:
    path = Path(path)
    # print(path.absolute())
    if path.exists():
        return
    mkdir(path)


def deleteDir(path: typing.Union[str, PathLike]) -> None:
    path = Path(path)
    if path.exists():
        rmtree(path)


def textWrite(path: typing.Union[str, PathLike], text: str = "") -> None:
    path = Path(path)
    if path.exists():
        if input(f"./{path} already exists. overwrite? y/N ") == "y":
            with open(path, "w") as file:
                file.write(text)
        else:
            print("skipping")
            return
    else:
        with open(path, "w") as file:
            file.write(text)


def jsonWrite(path: typing.Union[str, PathLike], obj: dict | list) -> None:
    path = Path(path)
    if path.exists():
        if input(f"./{path} already exists. overwrite? y/N ") == "y":
            with open(path, "w") as file:
                file.write(json.dumps(obj, indent=4))
        else:
            print("skipping")
            return
    else:
        with open(path, "w") as file:
            file.write(json.dumps(obj, indent=4))


def jsonLoad(path: typing.Union[str, PathLike]) -> dict | list:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)
    with open(path, "r") as file:
        return json.load(file)


TEMPLATE_SECRETS = jsonLoad(Path("configs/secretsTEMPLATE.json"))
TEMPLATE_PERSONAL = {} #TODO


def main() -> None:
    try:
        deleteDir("log/")
        createDir("log/")
        createDir("tmp/")
        createDir("runs/")
        jsonWrite(Path("configs/secrets.json"), TEMPLATE_SECRETS)
        jsonWrite(Path("configs/personal.json"), TEMPLATE_PERSONAL)
        print("setup done")
    except KeyboardInterrupt:
        print("halt")


if __name__ == "__main__":
    main()
