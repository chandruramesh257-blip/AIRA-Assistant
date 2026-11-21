import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("aira.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            due_date TEXT,
            status TEXT NOT NULL DEFAULT 'open',
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            business TEXT,
            requirement TEXT,
            status TEXT NOT NULL DEFAULT 'new',
            created_at TEXT NOT NULL
        );
        """
    )

    conn.commit()
    conn.close()


def now():
    return datetime.now().isoformat(timespec="seconds")


def save_message(role: str, content: str):
    conn = get_connection()
    conn.execute(
        "INSERT INTO messages (role, content, created_at) VALUES (?, ?, ?)",
        (role, content, now()),
    )
    conn.commit()
    conn.close()


def get_recent_messages(limit: int = 20):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT role, content FROM messages
        ORDER BY id DESC LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()

    return [
        {"role": row["role"], "content": row["content"]}
        for row in reversed(rows)
    ]


def create_note(title: str, content: str):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO notes (title, content, created_at) VALUES (?, ?, ?)",
        (title, content, now()),
    )
    conn.commit()
    note_id = cursor.lastrowid
    conn.close()
    return {"note_id": note_id, "title": title, "status": "saved"}


def search_notes(query: str):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, title, content, created_at
        FROM notes
        WHERE title LIKE ? OR content LIKE ?
        ORDER BY id DESC
        LIMIT 10
        """,
        (f"%{query}%", f"%{query}%"),
    ).fetchall()
    conn.close()

    return [dict(row) for row in rows]


def create_task(title: str, due_date: str | None = None):
    conn = get_connection()
    cursor = conn.execute(
        "INSERT INTO tasks (title, due_date, created_at) VALUES (?, ?, ?)",
        (title, due_date, now()),
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {"task_id": task_id, "title": title, "due_date": due_date, "status": "created"}


def list_tasks(status: str = "open"):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, title, due_date, status, created_at
        FROM tasks
        WHERE status = ?
        ORDER BY id DESC
        LIMIT 50
        """,
        (status,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def complete_task(task_id: int):
    conn = get_connection()
    cursor = conn.execute(
        "UPDATE tasks SET status = 'completed' WHERE id = ?",
        (task_id,),
    )
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    if updated == 0:
        return {"status": "not_found"}
    return {"task_id": task_id, "status": "completed"}


def create_lead(
    name: str,
    email: str | None = None,
    phone: str | None = None,
    business: str | None = None,
    requirement: str | None = None,
):
    conn = get_connection()
    cursor = conn.execute(
        """
        INSERT INTO leads
        (name, email, phone, business, requirement, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'new', ?)
        """,
        (name, email, phone, business, requirement, now()),
    )
    conn.commit()
    lead_id = cursor.lastrowid
    conn.close()
    return {"lead_id": lead_id, "name": name, "status": "lead_saved"}


def list_leads(status: str = "new"):
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT id, name, email, phone, business, requirement, status, created_at
        FROM leads
        WHERE status = ?
        ORDER BY id DESC
        LIMIT 50
        """,
        (status,),
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
