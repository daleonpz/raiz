# Copyright (c) 2025 Daniel Paredes (daleonpz)
# SPDX-License-Identifier: Apache-2.0

import sqlite3
from pathlib import Path

REQ_CACHE_DIR = Path(".req_cache")
REQ_CACHE_DIR.mkdir(exist_ok=True)
DB_FILE = REQ_CACHE_DIR / "requirements.db"

def db_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with db_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS requirements (
                uuid TEXT PRIMARY KEY,
                seq_no INTEGER UNIQUE,
                description TEXT NOT NULL,
                type TEXT NOT NULL,
                domain TEXT NOT NULL,
                linked_tests TEXT DEFAULT ''
        """)
        conn.commit()

def renumber_all():
    with db_conn() as conn:
        cur = conn.execute("SELECT uuid FROM requirements ORDER BY seq_no ASC")
        uuids = [row["uuid"] for row in cur.fetchall()]
        for i, uid in enumerate(uuids, start=1):
            conn.execute("UPDATE requirements SET seq_no = ? WHERE uuid = ?", (i, uid))
        conn.commit()

