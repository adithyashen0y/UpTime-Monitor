import os
import sqlite3
import time
import requests

DB_PATH = os.environ.get("DB_PATH", "uptime.db")
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "60"))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS checks (
                id               INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id          INTEGER NOT NULL,
                status           TEXT NOT NULL,
                status_code      INTEGER,
                response_time_ms INTEGER,
                checked_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def check_site(url):
    try:
        start = time.time()
        r = requests.get(url, timeout=10)
        ms = int((time.time() - start) * 1000)
        status = "UP" if r.status_code < 400 else "DOWN"
        return status, r.status_code, ms
    except requests.RequestException:
        return "DOWN", None, None


def run_checks():
    with get_db() as conn:
        sites = conn.execute("SELECT * FROM sites").fetchall()
        for site in sites:
            status, code, ms = check_site(site["url"])
            conn.execute(
                "INSERT INTO checks (site_id, status, status_code, response_time_ms) "
                "VALUES (?, ?, ?, ?)",
                (site["id"], status, code, ms),
            )
            print(f"{site['name']}: {status} ({code}, {ms} ms)")


if __name__ == "__main__":
    init_db()
    while True:
        run_checks()
        time.sleep(CHECK_INTERVAL)
