"""
NetSage AI — Database Layer
SQLite database with migration-ready schema for PostgreSQL upgrade.
"""

import aiosqlite
import os
import json
from datetime import datetime

DATABASE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "netsage.db")


async def get_db():
    """Get database connection."""
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    """Initialize database schema."""
    db = await get_db()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                symptom TEXT NOT NULL,
                topology_notes TEXT DEFAULT '',
                show_outputs TEXT DEFAULT '',
                expected_fault TEXT DEFAULT '',
                osi_layer TEXT DEFAULT '',
                concept TEXT DEFAULT '',
                severity TEXT DEFAULT 'Medium',
                status TEXT DEFAULT 'Open',
                created_at TEXT DEFAULT (datetime('now')),
                updated_at TEXT DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS diagnoses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                root_cause TEXT NOT NULL,
                confidence INTEGER NOT NULL DEFAULT 0,
                osi_layer TEXT DEFAULT '',
                evidence TEXT DEFAULT '[]',
                next_command TEXT DEFAULT '',
                fix_steps TEXT DEFAULT '[]',
                alternative_causes TEXT DEFAULT '[]',
                is_demo_mode INTEGER DEFAULT 0,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                diagnosis_id INTEGER NOT NULL,
                decision TEXT NOT NULL CHECK(decision IN ('accepted', 'edited', 'rejected')),
                edited_diagnosis TEXT DEFAULT '',
                reviewer_notes TEXT DEFAULT '',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
                FOREIGN KEY (diagnosis_id) REFERENCES diagnoses(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS responsible_ai_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                ai_diagnosis TEXT NOT NULL,
                human_correction TEXT NOT NULL,
                why_ai_wrong TEXT NOT NULL,
                final_diagnosis TEXT NOT NULL,
                lesson TEXT NOT NULL,
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS rule_check_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT NOT NULL,
                results TEXT NOT NULL DEFAULT '[]',
                created_at TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE
            );
        """)
        await db.commit()
    finally:
        await db.close()


async def execute_query(query: str, params: tuple = ()):
    """Execute a query and return results."""
    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        rows = await cursor.fetchall()
        await db.commit()
        return [dict(row) for row in rows]
    finally:
        await db.close()


async def execute_insert(query: str, params: tuple = ()):
    """Execute an insert query and return the last row id."""
    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.lastrowid
    finally:
        await db.close()


async def execute_update(query: str, params: tuple = ()):
    """Execute an update/delete query and return rows affected."""
    db = await get_db()
    try:
        cursor = await db.execute(query, params)
        await db.commit()
        return cursor.rowcount
    finally:
        await db.close()
