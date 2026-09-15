import os
from typing import Optional

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import Error


load_dotenv(override=True)


def _env_setting(name: str, default: str) -> str:
    return os.getenv(name, default).strip().strip('"').strip("'")


class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DatabaseConnection(metaclass=SingletonMeta):
    def __init__(self):
        self.connection = None

    def get_connection_config(self) -> dict:
        return {
            "host": _env_setting("MYSQL_HOST", "localhost"),
            "port": int(_env_setting("MYSQL_PORT", "3306")),
            "user": _env_setting("MYSQL_USER", "root"),
            "password": _env_setting("MYSQL_PASSWORD", ""),
            "database": _env_setting("MYSQL_DATABASE", "hr_analytics_oltp"),
            "autocommit": False,
            "connection_timeout": 30,
            "use_pure": True,
        }

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.get_connection_config())
            return self.connection
        except Error as exc:
            raise RuntimeError(f"Database connection failed: {exc}") from exc

    def get_connection(self):
        if self.connection is None or not self.connection.is_connected():
            self.connect()
        return self.connection

    def close(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            self.connection = None

    def execute_query(self, query: str, params: Optional[tuple] = None):
        try:
            cursor = self.get_connection().cursor(dictionary=True)
            cursor.execute(query, params or ())
            return cursor
        except Error as exc:
            raise RuntimeError(f"Query execution failed: {exc}") from exc
