import mysql.connector

class MySQLDatabase:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def __enter__(self):
        self.connection = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            self.connection.commit()
            self.connection.close()

    def create_table(self, table_name, column_definitions):
        cursor = self.connection.cursor()

        create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
        cursor.execute(create_table_query)

        cursor.close()

    def insert_data(self, table_name, data):
        cursor = self.connection.cursor()

        columns = ", ".join(data.keys())
        values = ", ".join("%s" for _ in data.values())

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
