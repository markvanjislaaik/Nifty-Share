import sqlite3
from settings import DatabaseConfig

class SQLiteDatabase:
    def __init__(self, db_file):
        self.db_file = DatabaseConfig.SQLITE_DB_FILENAME
        self.connection = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_file)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.commit()
            self.connection.close()

    def create_table(self, table_name, column_definitions):
        cursor = self.connection.cursor()

        create_table_query = f"CREATE TABLE {table_name} ({column_definitions})"
        cursor.execute(create_table_query)

        cursor.close()

    def insert_data(self, table_name, data):
        cursor = self.connection.cursor()

        columns = ", ".join(data.keys())
        values = ", ".join("?" for _ in data.values())

        insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        cursor.execute(insert_query, tuple(data.values()))

        cursor.close()

    def select_data(self, table_name, condition=None, columns="*"):
        cursor = self.connection.cursor()

        select_query = f"SELECT {columns} FROM {table_name}"
        if condition:
            select_query += f" WHERE {condition}"

        cursor.execute(select_query)
        results = cursor.fetchall()

        cursor.close()

        return results


if __name__ == '__main__':

    db_file = "sample_database.db"

    with SQLiteDatabase(db_file) as db:
        column_definitions = "id INTEGER PRIMARY KEY, " \
                            "sender_name VARCHAR(100), " \
                            "file_basename VARCHAR(100), " \
                            "sender_address VARCHAR(100), " \
                            "download_link TEXT, " \
                            "recipient_email VARCHAR(100), " \
                            "expiry_date DATETIME, " \
                            "file_size_mb REAL, " \
                            "files_list TEXT, " \
                            "date_added DATETIME DEFAULT CURRENT_TIMESTAMP"

        db.create_table("nifty_transfers", column_definitions)