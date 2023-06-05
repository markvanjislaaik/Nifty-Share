import os
import sqlite3
import mysql.connector

from settings import DatabaseConfig

class DatabaseFactory:
    @staticmethod
    def create_database(db_type: str, **kwargs):
        if db_type == "mysql":
            return MySQLDatabase(**kwargs)
        elif db_type == "sqlite":
            return SQLiteDatabase(**kwargs)
        else:
            raise ValueError("Invalid database type")


class Database:
    def create_table(self, table_name: str, column_definitions: str) -> None:
        cursor = self.connection.cursor()

        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
        cursor.execute(create_table_query)

        cursor.close()

    def insert_data(self, table_name: str, params: dict) -> None:

        params['table_name'] = table_name
        params['files_list'] = ", ".join(params['files_list'])

        cursor = self.connection.cursor()
        cursor.execute(self.insert_query, params)

        cursor.close()

    def select_data(self, table_name: str, condition: str=None, columns: str="*") -> list:
        cursor = self.connection.cursor()

        select_query = f"SELECT {columns} FROM {table_name}"
        if condition:
            select_query += f" WHERE {condition}"

        cursor.execute(select_query)
        results = cursor.fetchall()

        cursor.close()

        return results

class SQLiteDatabase(Database):
    def __init__(self, db_file: str) -> None:
        self.db_file = DatabaseConfig.SQLITE_DB_FILENAME
        self.connection = None

        self.insert_query = """
        INSERT INTO transfers
        (
            sender_name,
            file_basename,
            sender_address,
            download_link,
            recipient_email,
            expiry_date,
            file_size_bytes,
            files_list,
            date_added
        )
        VALUES
        (
            :sender_name,
            :file_basename,
            :sender_address,
            :download_link,
            :recipient_email,
            :expiry_date_dt,
            :file_size_bytes,
            :files_list,
            :local_datetime
        );
        """

    def __enter__(self) -> None:
        self.connection = sqlite3.connect(self.db_file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.connection:
            self.connection.commit()
            self.connection.close()
    

class MySQLDatabase(Database):
    def __init__(self, host: str, user: str, password: str, database: str) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.insert_query = """
            INSERT INTO transfers
            (
                sender_name,
                file_basename,
                sender_address,
                download_link,
                recipient_email,
                expiry_date,
                file_size_bytes,
                files_list
            )
            VALUES
            (
                %(sender_name)s,
                %(file_basename)s,
                %(sender_address)s,
                %(download_link)s,
                %(recipient_email)s,
                %(expiry_date_dt)s,
                %(file_size_bytes)s,
                %(files_list)s
            );
            """

    def __enter__(self) -> None:
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.connection:
            self.connection.commit()
            self.connection.close()


def get_db_connection():
    
    db_config = DatabaseConfig()

    if db_config.DB_TYPE == "mysql":
        mysql_db = DatabaseFactory.create_database(
            db_type="mysql",
            host=db_config.MYSQL_DB_HOST,
            user=db_config.MYSQL_DB_USERNAME,
            password=db_config.MYSQL_DB_PASSWORD,
            database=db_config.MYSQL_DB_NAME)

        with mysql_db as db:
            db.create_table("transfers", db_config.MYSQL_COLS)

        return mysql_db

    elif db_config.DB_TYPE == "sqlite":
        db_file=db_config.SQLITE_DB_FILENAME
        if not os.path.exists(db_file):

            sqlite_db = DatabaseFactory.create_database(
                db_type="sqlite",
                db_file=db_config.SQLITE_DB_FILENAME)

            with sqlite_db as db:
                db.create_table("transfers", db_config.SQLITE_COLS)

        else:
            sqlite_db = DatabaseFactory.create_database(
                db_type="sqlite",
                db_file=db_config.SQLITE_DB_FILENAME)
        return sqlite_db