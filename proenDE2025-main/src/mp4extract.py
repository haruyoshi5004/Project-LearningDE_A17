from pathlib import Path
from enum import IntEnum
from re import findall as reFindall
from datetime import datetime
from typing import Optional, TypeVar, overload
from shutil import rmtree
import os
from time import sleep
import asyncio

from logging import getLogger
from logging.config import dictConfig

from yaml import FullLoader, load as loadYaml
import cv2
from cv2.typing import MatLike

# hexdump -C PATH > tmp/test.txt

# TODO getcoordinate with startOffset and interval

logger = getLogger("BicycleCheck.mp4file")

T = TypeVar("T")
CHUNKSIZE = 130


class FileSizes(IntEnum):
    VID1 = 100663296
    VID3 = 301989888


class SeekSizes(IntEnum):
    VID1M = 100065228
    VID3M = 301391820


class Mp4UnrecognizableException(BaseException):
    pass


class Mp4FileException(BaseException):
    pass


class Mp4FileCoordinateDataInvalidException(BaseException):
    pass


singlecoordinateType = tuple[float, int, int, float, bool]
coordinateType = tuple[
    int, datetime, tuple[singlecoordinateType, singlecoordinateType] | None
]


class Mp4File(object):
    # ファイル名は一切固有のものではないので、送信された際にファイル名被りを起こす可能性がある。
    # 一意の名前をつけたフォルダに他の情報を含むjsonと一緒に入れるなどで対処すること → formの設計時に注意
    # というかそもそもファイル名に依存しているリスクについて
    path: Path
    cached_Coordinates: Optional[list[coordinateType]] = None

    def __init__(self, path: str | os.PathLike) -> None:
        path = Path(path)
        if not path.exists():
            raise Mp4FileException("file don't exist")
        self.path = path
        _file = open(self.path)
        _file.close()

    def getFileSize(self) -> FileSizes:
        size = os.path.getsize(self.path)
        match size:
            case FileSizes.VID1:
                return FileSizes.VID1
            case FileSizes.VID3:
                return FileSizes.VID3
            case _:
                raise Mp4UnrecognizableException(f"unknown file size: {size}")

    def getStartDate(self) -> datetime:
        filename = self.getFilenameParsed()
        return datetime.strptime("".join(filename[4:6]), "%y%m%d%H%M%S")

    def getStartDateFormat(self) -> str:
        """
        suitable for filename
        """
        startDate = self.getStartDate()
        return startDate.strftime("%Y%m%d-%H%M%S")

    def isHead(self) -> bool:
        return self.getFilenameParsed()[3] == "S"

    def getFilenameSerial(self) -> int:
        return int(self.getFilenameParsed()[6])

    def getFilenameParsed(self) -> tuple[str, str, str, str, str, str, str, str]:
        PETTERN = r"([APT])([GMD_])([T_])([S_])-(\d{6})-(\d{6})-(\d{6})([FR])\.MP4"
        return reFindall(PETTERN, str(self.path.name))[0]

    def getFilenameFormat(self) -> str:
        return f"{self.getStartDateFormat()}-{self.getFilenameSerial()}"

    def getVideoFile(self) -> cv2.VideoCapture:
        return cv2.VideoCapture(str(self.path.absolute()))

    def getStartPoint(self) -> SeekSizes:
        size = self.getFileSize()
        match size:
            case FileSizes.VID1:
                return SeekSizes.VID1M
            case FileSizes.VID3:
                return SeekSizes.VID3M
            case _:
                raise Mp4UnrecognizableException(
                    f"unknown file size: {size}"
                )  # ありえない

    @staticmethod
    def _parseCoordinate(chunk: bytes) -> coordinateType:
        SCANPETTERN_INITIAL = rb"(\d{8})([AV])(.{21})(.*)"
        SCANPETTERN_LATLNT = rb"(\d{2})([\d\.]{7})([NS])(\d{3})([\d\.]{7})([EW])"
        rawCoordinate = chunk[:50]
        scannedBase: tuple[bytes, bytes, bytes, bytes] = reFindall(
            SCANPETTERN_INITIAL, rawCoordinate
        )[0]
        index = int(scannedBase[0].decode())
        datestamp = datetime.strptime(scannedBase[3].decode()[4:], "%y%m%d%H%M%S.%f")
        coordinate: tuple[singlecoordinateType, singlecoordinateType] | None
        if scannedBase[1] == b"V":
            coordinate = None
        else:
            scanResult2: tuple[bytes, bytes, bytes, bytes, bytes, bytes] = reFindall(
                SCANPETTERN_LATLNT, scannedBase[2]
            )[0]
            lat_deg = int(scanResult2[0].decode())
            lat_minsec = float(scanResult2[1].decode())
            lat_min = int(lat_minsec // 1)
            lat_sec = lat_minsec % 1 * 60
            lat_dec = lat_deg + (lat_minsec / 60)
            lat_isNorth = scanResult2[2].decode() == "N"
            lnt_deg = int(scanResult2[3].decode())
            lnt_minsec = float(scanResult2[4].decode())
            lnt_min = int(lnt_minsec // 1)
            lnt_sec = lnt_minsec % 1 * 60
            lnt_dec = lnt_deg + (lnt_minsec / 60)
            lnt_isEast = scanResult2[5].decode() == "E"
            coordinate = (
                (
                    lat_dec,
                    lat_deg,
                    lat_min,
                    lat_sec,
                    lat_isNorth,
                ),
                (
                    lnt_dec,
                    lnt_deg,
                    lnt_min,
                    lnt_sec,
                    lnt_isEast,
                ),
            )
        return (
            index,
            datestamp,
            coordinate,
        )

    def getAllCoordinates(self, includeInvalid: bool = True) -> list[coordinateType]:
        # FIXME 出力されるフレーム量が不一定。 602と1802が正常なはずだが、803と1803が出力される
        CHUNKSIZE = 130
        if self.cached_Coordinates is not None:
            return self.cached_Coordinates
        startPoint = self.getStartPoint()
        result: list[coordinateType] = []
        with open(self.path, mode="rb") as file:
            file.seek(startPoint, os.SEEK_SET)
            header = file.read(6)
            if header != b"CSMDAT":
                raise Mp4UnrecognizableException(
                    f"couldn't recognize file. didn't read CSMDAT at {startPoint}"
                )
            file.read(34)
            count = 0
            invalid_count = 0
            while True:
                try:
                    chunk = file.read(CHUNKSIZE)
                    if chunk == (b" " * CHUNKSIZE):
                        break
                    count += 1
                    parsedCoordinate = self._parseCoordinate(chunk)
                    if parsedCoordinate[2] is None:
                        invalid_count += 1
                        if not includeInvalid:
                            continue
                    result.append(parsedCoordinate)
                except UnicodeDecodeError:
                    logger.error(f"UnicodeDecodeError at {self.path}:{count}")
                    continue
        logger.info(
            f"read coordinate of '{self.path.parent.name}/{self.path.name}'. valid rate: {count-invalid_count}/{count}"
        )
        self.cached_Coordinates = result
        return result

    def getIntervalCoordinates(
        self, intervalCount: int, startingOffset: int = 0, includeInvalid: bool = True
    ) -> list[coordinateType]:
        # FIXME 出力されるフレーム量が不一定。 602と1802が正常なはずだが、803と1803が出力される
        startPoint = self.getStartPoint()
        result: list[coordinateType] = []
        with open(self.path, mode="rb") as file:
            file.seek(startPoint, os.SEEK_SET)
            header = file.read(6)
            if header != b"CSMDAT":
                raise Mp4UnrecognizableException(
                    f"couldn't recognize file. didn't read CSMDAT at {startPoint}"
                )
            file.read(34)
            count = 0
            invalid_count = 0
            file.read(CHUNKSIZE * startingOffset)
            while True:
                try:
                    chunk = file.read(CHUNKSIZE)
                    if chunk == (b" " * CHUNKSIZE):
                        break
                    count += 1
                    parsedCoordinate = self._parseCoordinate(chunk)
                    if parsedCoordinate[2] is None:
                        invalid_count += 1
                        if not includeInvalid:
                            continue
                    result.append(parsedCoordinate)
                except UnicodeDecodeError:
                    logger.error(f"UnicodeDecodeError at {self.path}:{count}")
                    continue
                file.read(CHUNKSIZE * intervalCount)
        logger.info(
            f"read coordinate of '{self.path.parent.name}/{self.path.name}', by intervalCount {intervalCount}, startingOffset {startingOffset}. valid rate: {count-invalid_count}/{count}"
        )
        self.cached_Coordinates = result
        return result

    async def _extractFrame(self, frameIndex) -> Optional[MatLike]:
        videoFile = self.getVideoFile()
        videoFile.set(cv2.CAP_PROP_POS_FRAMES, frameIndex)
        ret, frame = videoFile.read()
        if ret:
            return frame
        else:
            logger.warning(
                f"couldn't load frame {frameIndex} of '{self.path.parent.name}/{self.path.name}'"
            )
            return None

    def extractFrames(self, step: int) -> list[Optional[MatLike]]:
        async def gather():
            videoFrames = self.getVideoFrameCount()
            tasks = []
            for i in range(0, videoFrames, step):
                tasks.append(asyncio.create_task(self._extractFrame(i)))
            return await asyncio.gather(*tasks)

        result = asyncio.run(gather())
        logger.info(
            f"extracted {len(result)}/{self.getVideoFrameCount()} frames of {self.path.name}, every {step} frames"
        )
        return result

    async def _writeFrame(self, frame: MatLike, filename: Path) -> Path:
        await asyncio.sleep(0)
        result = cv2.imwrite(str(filename), frame)
        await asyncio.sleep(0)
        if result:
            return filename
        else:
            raise Exception()  # TODO couldn't write file

    def writeFrames(
        self,
        targetDir: Path,
        frames: list[Optional[MatLike]],
        step: Optional[int] = None,
    ) -> list[Path]:
        FILESAFE = False
        if not FILESAFE:
            if targetDir.exists():
                rmtree(targetDir)
            os.mkdir(targetDir)
        if step is None:
            step = 1

        async def gather() -> list[Path]:
            tasks: list[asyncio.Task[Path]] = []
            frameCount = 0
            for frame in frames:
                frameCount += step
                if frame is None:
                    continue
                startDate = self.getStartDateFormat()
                filename = targetDir.joinpath(f"{startDate}_{frameCount}.jpg")
                tasks.append(asyncio.create_task(self._writeFrame(frame, filename)))
            return await asyncio.gather(*tasks)

        result = asyncio.run(gather())
        logger.info(f"written {len(frames)} frames of {self.path} into {targetDir}/")
        return result

    def getVideoFrameCount(self) -> int:
        return int(self.getVideoFile().get(cv2.CAP_PROP_FRAME_COUNT))

    def getVideoFps(self) -> float:
        # return self.getVideoFile().get(cv2.CAP_PROP_FPS)
        return 28.1018981018981

    def getVideoLength(self) -> float:
        frameRate = self.getVideoFps()
        frames = self.getVideoFrameCount()
        return frames / frameRate

    def getRatio(self, allCoordinates: Optional[list[coordinateType]] = None) -> float:
        # TODO overload
        if allCoordinates is None:
            allCoordinates = self.getAllCoordinates()
        return len(allCoordinates) / self.getVideoFrameCount()

    def getTimePerCoordinate(
        self, coordinates: Optional[list[coordinateType]] = None
    ) -> float:
        if coordinates is None:
            coordinates = self.getAllCoordinates()
        return self.getVideoLength() / len(coordinates)


def getItemByPercent(items: list[T], percent: float) -> T:
    # percent must be between 0.0 ~ 1.0
    size = len(items)
    return items[round(size * percent)]


def getPercentOfItem(items: list[T], item: T) -> float:
    index = items.index(item)
    size = len(items)
    return index / size


if __name__ == "__main__":
    with open(Path("configs/log_conf.yaml"), "r", encoding="UTF-8") as configFile:
        dictConfig(loadYaml(configFile.read(), FullLoader))
    BASEDIR = Path("tmp/")
    intervalTime = 30
    files = list(BASEDIR.iterdir())
    for file in files[:]:
        if not file.is_file():
            continue
        if not file.suffix == ".MP4":
            continue
        mp4File = Mp4File(file)
        allCoordinates = mp4File.getAllCoordinates()
        someCoordinates = mp4File.getIntervalCoordinates(9, 0)
        print(mp4File.getVideoLength())
        print(mp4File.getTimePerCoordinate(allCoordinates))
        print(mp4File.getTimePerCoordinate(someCoordinates))
