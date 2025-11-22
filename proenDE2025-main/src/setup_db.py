from pathlib import Path
from yaml import load as loadYaml, FullLoader

from mysql.connector.errors import ProgrammingError as MysqlProgrammingError

from crud import getConnectionToServer, getConnectionToDB, getDBConfig

def setUpDB():
    print("setup db start")
    dbConfig = getDBConfig()
    conn = getConnectionToServer()
    cursor = conn.cursor()
    try:
        # TODO userがいない場合にuserを作る
        cursor.execute(f"DROP DATABASE ...") #TODO データベースを毎度削除するクエリ
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {dbConfig["database"]}")
        # TODO userに対してgrant
    except MysqlProgrammingError as e:
        conn.rollback()
    finally:
        conn.commit()
        cursor.close()
    try:
        print("setup tables start")
        conn = getConnectionToDB(conn)
        cursor = conn.cursor()
        # 管区テーブル
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS district_info(district_id INT PRIMARY KEY AUTO_INCREMENT,name VARCHAR(10) NOT NULL)"
        )
        # 自転車テーブル
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS bike_info(bicycle_id INT PRIMARY KEY AUTO_INCREMENT,handled_flg BOOLEAN NOT NULL)"
        )
        # ユーザーテーブル
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS user_info(user_id INT PRIMARY KEY AUTO_INCREMENT,name VARCHAR(10) NOT NULL,email VARCHAR(50)  NOT NULL,password VARCHAR(100) NOT NULL)"
        )
        # 車両テーブル
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS car_info(vehicle_id INT PRIMARY KEY AUTO_INCREMENT,vehicle_name VARCHAR(20),district_id INT NOT NULL,FOREIGN KEY(district_id) REFERENCES district_info(district_id))"
        )
        # 走行テーブル
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS run_info(runtime_id INT PRIMARY KEY AUTO_INCREMENT,vehicle_id INT NOT NULL,user_id INT NOT NULL,Run_start DATETIME NOT NULL,Run_fin DATETIME NOT NULL,FOREIGN KEY(vehicle_id) REFERENCES car_info(vehicle_id),FOREIGN KEY(user_id) REFERENCES user_info(user_id))"
        )
        # 検出テーブル
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS kensys_info(instance_id INT PRIMARY KEY AUTO_INCREMENT,bicycle_id INT NOT NULL,runtime_id INT NOT NULL,detection_time DATETIME NOT NULL,x_chunk INT NOT NULL,y_chunk INT NOT NULL,x_fractional FLOAT NOT NULL,y_fractional FLOAT NOT NULL,image_path VARCHAR(255) NOT NULL,color VARCHAR(10) NOT NULL,has_basket BOOLEAN NOT NULL,has_childseat BOOLEAN NOT NULL,FOREIGN KEY(bicycle_id) REFERENCES bike_info(bicycle_id),FOREIGN KEY(runtime_id) REFERENCES run_info(runtime_id))"
        )
        conn.commit()
        print("✅ All tables created and test data inserted successfully.")
    except MysqlProgrammingError as e:
        print("error happened: ", e.msg)
        print("rollbacking")
        conn.rollback()
    finally:
        print("committing...")
        conn.commit()
        cursor.close()
    conn.close()
    print("done")


if __name__ == "__main__":
    setUpDB()
