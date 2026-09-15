from __future__ import annotations

import subprocess
from pathlib import Path

import mysql.connector


def _normalize_mysql_script(script_text: str) -> str:
    lines = []
    for raw_line in script_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.upper().startswith("DELIMITER"):
            continue
        if line.endswith("//"):
            line = line[:-2].strip()
        if line.endswith(";"):
            lines.append(line)
        else:
            lines.append(line + ";")
    return "\n".join(lines)


def _execute_with_mysql_cli(script_path: str | Path, host: str, port: int, user: str, password: str, database: str | None):
    path = Path(script_path)
    mysql_bin = Path(r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe")
    if not mysql_bin.exists():
        raise FileNotFoundError(f"MySQL CLI executable not found at: {mysql_bin}")

    cmd = [
        str(mysql_bin),
        f"--host={host}",
        f"--port={port}",
        f"--user={user}",
        f"--password={password}",
    ]
    if database:
        cmd.append(database)

    with path.open("r", encoding="utf-8") as sql_file:
        completed = subprocess.run(cmd, stdin=sql_file, capture_output=True, text=True)

    if completed.returncode != 0:
        raise RuntimeError(f"MySQL CLI execution failed: {completed.stderr.strip() or completed.stdout.strip()}")
    return completed


def execute_sql_script(
    script_path: str | Path,
    host: str = "localhost",
    port: int = 3306,
    user: str = "root",
    password: str = "",
    database: str | None = None,
):
    path = Path(script_path)
    if not path.exists():
        raise FileNotFoundError(f"MySQL script not found: {path}")

    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
    )
    try:
        TryCursor = conn.cursor()
        try:
            result = TryCursor.execute(_normalize_mysql_script(path.read_text(encoding="utf-8")), multi=True)
            if result is not None:
                for _ in result:
                    pass
            if hasattr(conn, "commit"):
                conn.commit()
            return TryCursor
        except Exception:
            if hasattr(conn, "close"):
                conn.close()
            conn = None
            return _execute_with_mysql_cli(path, host, port, user, password, database)
    finally:
        if conn is not None and hasattr(conn, "close"):
            conn.close()
