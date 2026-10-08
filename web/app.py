import os
import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)
DB_PATH = os.environ.get("DB_PATH", "uptime.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sites (
                id   INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url  TEXT NOT NULL
            )
        """)
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


@app.route("/")
def home():
    with get_db() as conn:
        sites = conn.execute("""
            SELECT s.id, s.name, s.url,
                   c.status, c.status_code, c.response_time_ms, c.checked_at,
                   (SELECT ROUND(100.0 * SUM(CASE WHEN status = 'UP' THEN 1 ELSE 0 END) / COUNT(*), 1)
                      FROM checks WHERE site_id = s.id) AS uptime
            FROM sites s
            LEFT JOIN checks c
              ON c.id = (SELECT MAX(id) FROM checks WHERE site_id = s.id)
        """).fetchall()
    return render_template("index.html", sites=sites)


@app.route("/add", methods=["POST"])
def add_site():
    name = request.form["name"]
    url = request.form["url"]
    with get_db() as conn:
        conn.execute("INSERT INTO sites (name, url) VALUES (?, ?)", (name, url))
    return redirect("/")


@app.route("/delete/<int:site_id>", methods=["POST"])
def delete_site(site_id):
    with get_db() as conn:
        conn.execute("DELETE FROM checks WHERE site_id = ?", (site_id,))
        conn.execute("DELETE FROM sites WHERE id = ?", (site_id,))
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
