from src.hr_analytics.db_manager import DatabaseConnection


def test_database_connection_from_env_values(monkeypatch):
    monkeypatch.setenv("MYSQL_HOST", "db.example.com")
    monkeypatch.setenv("MYSQL_PORT", "3307")
    monkeypatch.setenv("MYSQL_USER", "hr_user")
    monkeypatch.setenv("MYSQL_PASSWORD", "secret")
    monkeypatch.setenv("MYSQL_DATABASE", "warehouse_db")

    config = DatabaseConnection().get_connection_config()

    assert config["host"] == "db.example.com"
    assert config["port"] == 3307
    assert config["user"] == "hr_user"
    assert config["database"] == "warehouse_db"


def test_database_connection_is_singleton():
    first = DatabaseConnection()
    second = DatabaseConnection()

    assert first is second


def test_mysql_script_runner_executes_normalized_sql(monkeypatch):
    from src.hr_analytics.mysql_bootstrap import execute_sql_script

    class FakeCursor:
        def __init__(self):
            self.executed = []

        def execute(self, script, multi=False):
            self.executed.append((script, multi))

    class FakeConnection:
        def __init__(self):
            self.cursor_obj = FakeCursor()

        def cursor(self):
            return self.cursor_obj

    fake_conn = FakeConnection()
    monkeypatch.setattr("src.hr_analytics.mysql_bootstrap.mysql.connector.connect", lambda **kwargs: fake_conn)

    execute_sql_script("sql/03_etl_stored_procedures.sql", host="localhost", user="root", password="", database="hr_analytics_warehouse")

    assert fake_conn.cursor_obj.executed
    assert "DELIMITER" not in fake_conn.cursor_obj.executed[0][0]
    assert "CREATE PROCEDURE IF NOT EXISTS sp_load_dim_employee" in fake_conn.cursor_obj.executed[0][0]
