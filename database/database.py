from settings import DatabaseConfig

class DatabaseFactory:
    @staticmethod
    def create_database(db_type, **kwargs):
        if db_type == "mysql":
            from database.mysql_database import MySQLDatabase
            return MySQLDatabase(**kwargs)
        elif db_type == "sqlite":
            from database.sqlite_database import SQLiteDatabase
            return SQLiteDatabase(**kwargs)
        else:
            raise ValueError("Invalid database type")