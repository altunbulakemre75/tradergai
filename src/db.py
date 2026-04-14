from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "tradergai.db"


def _conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def init_db() -> None:
    with _conn() as con:
        con.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id   INTEGER PRIMARY KEY,
                username  TEXT,
                joined_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS watchlist (
                user_id INTEGER,
                ticker  TEXT,
                PRIMARY KEY (user_id, ticker)
            );
        """)


def ensure_user(user_id: int, username: str | None) -> None:
    with _conn() as con:
        con.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?,?)",
            (user_id, username),
        )


def add_ticker(user_id: int, ticker: str) -> bool:
    """Returns True if added, False if already exists."""
    try:
        with _conn() as con:
            con.execute(
                "INSERT INTO watchlist (user_id, ticker) VALUES (?,?)",
                (user_id, ticker.upper()),
            )
        return True
    except sqlite3.IntegrityError:
        return False


def remove_ticker(user_id: int, ticker: str) -> bool:
    """Returns True if removed, False if wasn't there."""
    with _conn() as con:
        cur = con.execute(
            "DELETE FROM watchlist WHERE user_id=? AND ticker=?",
            (user_id, ticker.upper()),
        )
        return cur.rowcount > 0


def get_watchlist(user_id: int) -> list[str]:
    with _conn() as con:
        rows = con.execute(
            "SELECT ticker FROM watchlist WHERE user_id=? ORDER BY ticker",
            (user_id,),
        ).fetchall()
        return [r[0] for r in rows]


def get_all_subscribed_users() -> dict[int, list[str]]:
    """Returns {user_id: [tickers]} for all users with non-empty watchlists."""
    with _conn() as con:
        rows = con.execute(
            "SELECT user_id, ticker FROM watchlist ORDER BY user_id"
        ).fetchall()
    result: dict[int, list[str]] = {}
    for uid, ticker in rows:
        result.setdefault(uid, []).append(ticker)
    return result
