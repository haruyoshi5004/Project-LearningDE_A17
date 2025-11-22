from pathlib import Path
from json import load
from typing import List, Dict, Any, Optional, cast,Union

from logging import getLogger

from mysql.connector import connect
from mysql.connector.pooling import PooledMySQLConnection
from mysql.connector.abstracts import MySQLConnectionAbstract
from mysql.connector.errors import (
    ProgrammingError as MysqlProgrammingError,
    DatabaseError,
)

LOGGER = getLogger("BicycleCheck.db")


def getDBConfig() -> dict[str, str | dict[str, str]]:
    filepath = Path("configs/secrets.json")
    try:
        with open(filepath, "r") as file:
            try:
                dbconfig = load(file)["db"]
            except KeyError as e:
                LOGGER.error("DB config doesn't exist!")
                raise e
    except FileNotFoundError as e:
        LOGGER.error("secrets config file doesn't exist!")
        raise e
    return dbconfig


def getConnectionToServer():
    dbconfig = getDBConfig()
    try:
        return connect(
            host=dbconfig["host"],
            user=dbconfig["user"],
            password=dbconfig["password"],
        )
    except DatabaseError as e:
        LOGGER.error(f"can't connect to DB! reason: {e.msg}")
        raise e


def getConnectionToDB(
    dbConnection: Optional[PooledMySQLConnection | MySQLConnectionAbstract] = None,
):
    if dbConnection is None:
        dbConnection = getConnectionToServer()
    try:
        dbconfig = getDBConfig()
        dbConnection.connect(database=dbconfig["database"])
        return dbConnection
    except DatabaseError as e:
        LOGGER.error(f"can't connect to DB! reason: {e.msg}")
        raise e


def get_select(
    query: str,
    conn: Optional[PooledMySQLConnection | MySQLConnectionAbstract] = None,
) -> List[Dict[str, Any]]:
    conn = getConnectionToDB(conn)
    try:
        cursor = conn.cursor()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
    except MysqlProgrammingError as e:
        LOGGER.error(f"couldn't run a query: {query}. reason: {e.msg}")
        conn.rollback()
    finally:
        data = cast(List[Dict[str, Any]], cursor.fetchall())
        cursor.close()
        conn.close()
    return data

def insert_query(
    query: str,
    params: Optional[Union[tuple[Any, ...], dict[str, Any]]] = None,
    conn: Optional[PooledMySQLConnection | MySQLConnectionAbstract] = None,
) -> Optional[int]:
    conn = getConnectionToDB(conn)
    last_id: Optional[int] = None
    try:
        cursor = conn.cursor()
        cursor = conn.cursor(dictionary=True)
        if params is not None:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        conn.commit()
        last_id = cursor.lastrowid
    except MysqlProgrammingError as e:
        LOGGER.error(f"Couldn't run query: {query}. reason: {e.msg}")
        conn.rollback()
    finally:
        LOGGER.warning(f"Could run query!")
        cursor.close()
        conn.close()
    return last_id

def delete_db(
    conn: Optional[PooledMySQLConnection | MySQLConnectionAbstract] = None,
):
    dbConfig = getDBConfig()
    dbName = dbConfig["db"]["database"]  # type:ignore
    conn = getConnectionToDB(conn)
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {dbName}")
    cursor.close()
    LOGGER.warning("deleted database!")
    conn.close()
