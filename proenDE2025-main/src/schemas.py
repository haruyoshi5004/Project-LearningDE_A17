"""
スキーマ。fastAPIが使用するほか、各種機能にアクセスできる

通常のpythonクラスではなく、pydantic.BaseModelクラスを継承し実装する。
BaseModelクラスでは、通常のpythonクラス以上に強力な型チェックが行われるため、問題が発生しにくい。
実装方法については以下など。
https://zenn.dev/sh0nk/books/537bb028709ab9/viewer/2c02d7
"""

from __future__ import annotations
from typing import Any
from abc import ABC, abstractmethod
from datetime import datetime

from logging import getLogger

from fastapi import Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.exceptions import HTTPException
from pydantic import ValidationError
from pydantic import BaseModel, Field

from crud import getConnectionToDB, DatabaseError, get_select, insert_query
import auth


logger = getLogger("bicyclecheck.schemas")


"""
sqlデータベースに接続
"""


def connectToDB():
    try:
        conn = getConnectionToDB()
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR) from e
    return conn


"""
sqlデータベースに接続する抽象クラス
"""


class SqlObject(ABC):

    @classmethod
    @abstractmethod
    def getTableName(cls) -> str:
        """
        DB上のテーブル名を取得する
        """

        raise NotImplementedError()

    @classmethod
    @abstractmethod
    def getOne(cls, id: int) -> Any | None:
        """
        指定されたidを元に、DB上のレコードを一つ取得する (cRud)
        """
        f"SELECT * FROM {cls.getTableName()} where id={id} LIMIT 1"

    # @classmethod
    # @abstractmethod
    # def getAll(cls) -> list:
    #     """
    #     DBのテーブルから全ての要素を取得する (cRud)
    #     """
    #     f"SELECT * FROM {cls.getTableName()}"

    @abstractmethod
    def create(self) -> None:
        """
        スキーマインスタンスを元に、DB上にレコードを追加する (Crud)
        """

    # def update(self) -> None:
    #     """
    #     スキーマインスタンスを元に、DB上のレコードを更新する (crUd)
    #     """

    # def delete(self) -> None:
    #     """
    #     スキーマインスタンスのidを元に、DB上のレコードを削除する (cruD)
    #     """


class Schema(BaseModel, SqlObject):
    """
    スキーマの抽象クラス。
    """

    pass


class Bicycle(Schema):
    """
    自転車クラス。DB上のbike_infoテーブルと対応。
    """

    bicycle_id: int = Field(alias="bicycle_id")
    handled_flg: bool

    @classmethod
    def getTableName(cls) -> str:
        return "bike_info"

    def create(self) -> None:
        query = f"INSERT INTO {self.getTableName()} ( handled_flg ) VALUES (%s)"
        value = (self.handled_flg,)
        conn = connectToDB()
        insert_query(query, value, conn)

    @classmethod
    def getOne(
        cls,
        id: int,
    ) -> Bicycle | None:
        """
        指定されたidを元に、bike_infoテーブルからデータを一つ取得し、Bicycleスキーマのインスタンスにする。
        """
        conn = connectToDB()
        query = f"SELECT * FROM {cls.getTableName()} WHERE bicycle_id={id}"
        rows: list[dict] = get_select(query, conn)
        if rows and isinstance(rows, list):
            try:
                return Bicycle(**rows[0])
            except ValidationError as e:
                raise ValueError(f"failed to validate data: {e}") from e
        return None

    def getDetects(self) -> list[BicycleDetect]:
        """
        この自転車idに紐づいている自転車発見事例を全て取得する
        """
        return BicycleDetect.getByBicycleId(self.bicycle_id)


class BicycleDetect(Schema):
    """
    自転車検出事例クラス。
    座標情報を扱う。
    座標は、DB内では[チャンク座標 + 端数座標]形態で、この :class:`BicycleDetect` クラス内では実座標形態で扱う。
    - 静的メソッド
        1. 実座標を[チャンク座標 + 端数座標]に変換する純粋関数
        2. [チャンク座標 + 端数座標]を実座標に変換する純粋関数
    - クラスメソッド
        1. 特定の座標に近い検出事例を全て抜き出す。
    """

    instance_id: int = Field(...)
    bicycle_id: int = Field(...)
    runtime_id: int = Field(...)
    detection_time: datetime = Field(...)
    coordinate_x: float = Field(...)
    coordinate_y: float = Field(...)
    image_path: str = Field(...)
    color: str = Field(...)
    has_basket: bool = Field(...)
    has_childseat: bool = Field(...)

    def create(self) -> None:
        x_chunk, x_fractional = self.coordinateActualToChunked(self.coordinate_x)
        y_chunk, y_fractional = self.coordinateActualToChunked(self.coordinate_y)
        query = f"INSERT INTO {self.getTableName()}(bicycle_id,runtime_id,detection_time,x_chunk,y_chunk,x_fractional,y_fractional,image_path,color,has_basket,has_childseat) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        value = (
            self.bicycle_id,
            self.runtime_id,
            self.detection_time,
            x_chunk,
            y_chunk,
            x_fractional,
            y_fractional,
            self.image_path,
            self.color,
            self.has_basket,
            self.has_childseat,
        )
        conn = connectToDB()
        insert_query(query, value, conn)

    @classmethod
    def getTableName(cls) -> str:
        return "kensys_info"

    @classmethod
    def coordinateActualToChunked(cls, coordinateActual: float) -> tuple[int, float]:
        raise NotImplementedError()

    @classmethod
    def coordinateChunkedToActual(cls, chunkedCoordinate: tuple[int, float]) -> float:
        raise NotImplementedError()

    @classmethod
    def getOne(cls, id: int) -> BicycleDetect | None:
        """
        指定されたidを元に、bike_infoテーブルからデータを一つ取得し、Bicycleスキーマのインスタンスにする。
        DB上では座標はチャンク番号と端数番号に分解されているので、 coordinateChunkedToActualを利用して実座標に変換すること。
        """
        conn = connectToDB()
        query = f"SELECT * FROM {cls.getTableName()} WHERE instance_id = {id} LIMIT 1"
        rows: list[dict] = get_select(query, conn)
        if rows and isinstance(rows, list):
            return BicycleDetect(**rows[0])
        return None

    @classmethod
    def getByBicycleId(cls, bicycleId) -> list[BicycleDetect]:
        """
        DB上から、特定の自転車idに紐づいている発見事例レコードを全て取得する
        """
        conn = connectToDB()
        query = f"SELECT * FROM {cls.getTableName()} where bicycle_id={bicycleId}"
        result: list[BicycleDetect] = []
        rows: list[dict] = get_select(query, conn)
        for row in rows:
            result.append(BicycleDetect(**row))
        return result

    @classmethod
    def getByRuntimeId(cls, runtime_id: int) -> list[BicycleDetect]:
        conn = connectToDB()
        query = f"SELECT * FROM {cls.getTableName()} WHERE runtime_id = {runtime_id}"
        result: list[BicycleDetect] = []
        rows: list[dict] = get_select(query, conn)
        for row in rows:
            result.append(BicycleDetect(**row))
        return result

    @classmethod
    def getByCoordinates(
        cls, coordinate_x: float, coordinate_y: float
    ) -> list[BicycleDetect]:
        """
        指定された座標に近い自転車検出事例を全て取得する。
        「近い座標」の考慮にはチャンク座標を用いる。
        """
        coordinate_chunk_x: int = cls.coordinateActualToChunked(coordinate_x)[0]
        coordinate_chunk_y: int = cls.coordinateActualToChunked(coordinate_y)[0]
        f"SELECT * FROM {cls.getTableName()} WHERE ..."  # TODO クエリを完成させる

    def getBicycle(self) -> Bicycle | None:
        """
        自身の持つ自転車idの紐づく自転車を取得する
        """
        bicycle = Bicycle.getOne(self.bicycle_id)
        if bicycle is None:
            logger.warning(
                "bicycleDetect: %s has tried to access bicycle %s despite its None",
                self.instance_id,
                self.bicycle_id,
            )
        return bicycle

    def getNearBicycleDetects(self) -> list[BicycleDetect]:
        """
        自身の座標に近い自転車検出事例を全て取得する。
        自身は除外。
        """
        return self.getByCoordinates(self.coordinate_x, self.coordinate_y)


class Area(Schema):
    """
    管区クラス。
    """

    district_id: int = Field(...)
    name: str = Field(...)

    @classmethod
    def getTableName(cls) -> str:
        return "district_info"

    def create(self):
        query = f"INSERT INTO {self.getTableName()}(name) VALUES (%s)"
        value = (self.name,)
        conn = connectToDB()
        insert_query(query, value, conn)

    @classmethod
    def getOne(cls, id: int) -> Area | None:
        conn = connectToDB()
        query = f"SELECT * FROM {cls.getTableName()} WHERE district_id = {id} LIMIT 1"
        rows: list[dict] = get_select(query, conn)
        if rows and isinstance(rows, list):
            return Area(**rows[0])
        return None

    def getCars(self) -> list[Car]:
        """
        この管区に紐づく車両クラスを全て取得する
        """
        return Car.getByAreaId(self.district_id)


class Car(Schema):
    """
    車両クラス。
    """

    vehicle_id: int = Field(...)
    vehicle_name: int = Field(...)
    district_id: int = Field(...)

    @classmethod
    def getTableName(cls) -> str:
        return "car_info"

    def create(self):
        query = f"INSERT INTO {self.getTableName()}(vehicle_name,district_id) VALUES (%s,%s)"
        value = (
            self.vehicle_name,
            self.district_id,
        )
        conn = connectToDB()
        insert_query(query, value, conn)

    @classmethod
    def getOne(cls, id: int) -> Car | None:
        conn = connectToDB()
        query = f"SELECT * FROM {cls.getTableName()} WHERE vehicle_id = {id} LIMIT 1"
        rows: list[dict] = get_select(query, conn)
        if rows and isinstance(rows, list):
            return Car(**rows[0])
        return None

    @classmethod
    def getByAreaId(cls, areaId: int) -> list[Car]:
        """
        特定の管区に紐づく車両を全て取得する
        """
        conn = connectToDB()
        query = f"SELECT * FROM {cls.getTableName()} WHERE district_id = {areaId}"
        result: list[Car] = []
        rows: list[dict] = get_select(query, conn)
        for row in rows:
            result.append(Car(**row))
        return result

    def getRuns(self) -> list[Run]:
        """
        この車両に紐づく走行を全て取得する
        """
        return Run.getByCarId(self.vehicle_id)


class Run(Schema):
    """
    走行
    """

    runtime_id: int = Field(...)
    vehicle_id: int = Field(...)
    user_id: int = Field(...)
    Run_start: datetime = Field(...)
    Run_fin: datetime = Field(...)

    @classmethod
    def getTableName(cls) -> str:
        return "run_info"

    def create(self):
        query = f"INSERT INTO {self.getTableName()}(vehicle_id,user_id,Run_start,Run_fin) VALUES (%s,%s,%s,%s)"
        value = (
            self.vehicle_id,
            self.user_id,
            self.Run_start,
            self.Run_fin,
        )
        conn = connectToDB()
        insert_query(query, value, conn)

    @classmethod
    def getOne(cls, id: int) -> Run | None:
        conn = connectToDB()
        query = f"SELECT * FROM {cls.getTableName()} WHERE runtime_id = {id} LIMIT 1"
        rows: list[dict] = get_select(query, conn)
        if rows and isinstance(rows, list):
            return Run(**rows[0])
        return None

    @classmethod
    def getByCarId(cls, carId: int) -> list[Run]:
        """
        特定の車両に紐づく走行を全て取得する
        """
        conn = connectToDB()
        query = f"SELECT * FROM {cls.getTableName()} WHERE vehicle_id = {carId}"
        result: list[Run] = []
        rows: list[dict] = get_select(query, conn)
        for row in rows:
            result.append(Run(**row))
        return result


class User(BaseModel):
    """
    ユーザー基底クラス。
    """

    user_id: int = Field(...)
    name: str = Field(...)
    district_id: int = Field(...)
    email: str = Field(...)

    @classmethod
    def login(cls, form: OAuth2PasswordRequestForm = Depends()) -> "AccessToken":
        if not auth.AuthUser(form.username, form.password):
            logger.info("login attempt to '%s'. fail", form.username)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        logger.info("login attempt to %s", form.username)
        tokenbody = auth.generateToken(form.username)
        return AccessToken(access_token=tokenbody, token_type="bearer")

    @classmethod
    def require(cls, user: User | None = Depends(auth.getCurrentUser)) -> User | None:
        return user


class UserSql(User, Schema):
    """
    ユーザーのDB寄りクラス。
    """

    hashedPassword: str = Field(..., alias="password")

    @classmethod
    def getTableName(cls) -> str:
        return "user_info"

    def create(self):
        query = (
            f"INSERT INTO {self.getTableName()}(name,email,password) VALUES (%s,%s,%s)"
        )
        value = (self.name, self.email, self.hashedPassword)

    @classmethod
    def getOne(cls, email: str) -> UserSql | None:
        conn = connectToDB()
        query = f"SELECT * FROM {cls.getTableName()} WHERE email = '{email}' LIMIT 1"
        rows: list[dict] = get_select(query, conn)
        if rows and isinstance(rows, list):
            user = UserSql(**rows[0])
            return user
        return None
    def asUser(self) -> User:
        return User(**self.model_dump())

class AccessToken(BaseModel):
    access_token: str
    token_type: str


if __name__ == "__main__":
    # Bicycle(bicycle_id=1, handled_flg=True).create()
    user = UserSql(
        user_id=1,
        name="johndoe",
        district_id=1,
        email="test@example.com",
        password=auth.hashPassword("test"),
    ).create()
    # User.login()
    # BicycleDetect(**{})
    # Area(**{})
    # Car(**{})
    # Run(**{})
    # User(**{})
