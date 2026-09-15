import os
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv


def setting(name: str) -> str:
    return os.getenv(name, "").strip().strip('"').strip("'")


def main() -> int:
    load_dotenv(Path(__file__).with_name(".env"), override=True)

    required_settings = (
        "MYSQL_HOST",
        "MYSQL_PORT",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DATABASE",
    )
    missing_settings = [name for name in required_settings if not setting(name)]
    if missing_settings:
        print(f"Missing environment settings: {', '.join(missing_settings)}")
        return 1

    connection = None
    try:
        connection = mysql.connector.connect(
            host=setting("MYSQL_HOST"),
            port=int(setting("MYSQL_PORT")),
            user=setting("MYSQL_USER"),
            password=setting("MYSQL_PASSWORD"),
            database=setting("MYSQL_DATABASE"),
            connection_timeout=10,
            use_pure=True,
        )
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print(f"Connection: OK ({setting('MYSQL_HOST')})")
        print(f"Database: {setting('MYSQL_DATABASE')}")
        print(f"SELECT 1: {cursor.fetchone()[0]}")

        checks = {
            "OLTP employees": "SELECT COUNT(*) FROM hr_analytics_oltp.employees",
            "OLTP reviews": "SELECT COUNT(*) FROM hr_analytics_oltp.reviews",
            "Warehouse employees": "SELECT COUNT(*) FROM defaultdb.dim_employee",
            "Warehouse facts": "SELECT COUNT(*) FROM defaultdb.fact_performance_reviews",
            "Warehouse projects": "SELECT COUNT(*) FROM defaultdb.dim_project",
        }
        for label, query in checks.items():
            cursor.execute(query)
            print(f"{label}: {cursor.fetchone()[0]}")
        cursor.close()
        return 0
    except (ValueError, mysql.connector.Error) as exc:
        print(f"Connection: FAILED ({exc})")
        return 1
    finally:
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    sys.exit(main())