"""Repositories: the ONLY place where SQL lives.

Rules:
- every query is parameterised (never build SQL with f-strings from user data);
- repositories never commit: the caller (service) decides the transaction, e.g.
      with transaction(conn):   # commits on success, rolls back on error
          repo.add(conn, ...)
"""
from __future__ import annotations

import sqlite3
from typing import Optional

from app.models import Member, Project, StatusHistory, Task


# ----------------------------------------------------------------- projects
class ProjectRepository:
    def add(self, conn: sqlite3.Connection, p: Project) -> int:
        cur = conn.execute(
            "INSERT INTO projects (name, start_date, due_date) VALUES (?, ?, ?)",
            (p.name, p.start_date, p.due_date),
        )
        return cur.lastrowid

    def get(self, conn: sqlite3.Connection, project_id: int) -> Optional[Project]:
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (project_id,)).fetchone()
        return Project(**dict(row)) if row else None

    def get_by_name(self, conn: sqlite3.Connection, name: str) -> Optional[Project]:
        row = conn.execute("SELECT * FROM projects WHERE name = ?", (name,)).fetchone()
        return Project(**dict(row)) if row else None

    def list_all(self, conn: sqlite3.Connection) -> list[Project]:
        rows = conn.execute("SELECT * FROM projects ORDER BY name").fetchall()
        return [Project(**dict(r)) for r in rows]

    def update(self, conn: sqlite3.Connection, p: Project) -> None:
        conn.execute(
            "UPDATE projects SET name = ?, start_date = ?, due_date = ? WHERE id = ?",
            (p.name, p.start_date, p.due_date, p.id),
        )

    def delete(self, conn: sqlite3.Connection, project_id: int) -> None:
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))


# ------------------------------------------------------------------ members
class MemberRepository:
    def add(self, conn: sqlite3.Connection, m: Member) -> int:
        cur = conn.execute("INSERT INTO members (name) VALUES (?)", (m.name,))
        return cur.lastrowid

    def get(self, conn: sqlite3.Connection, member_id: int) -> Optional[Member]:
        row = conn.execute("SELECT * FROM members WHERE id = ?", (member_id,)).fetchone()
        return Member(**dict(row)) if row else None

    def get_by_name(self, conn: sqlite3.Connection, name: str) -> Optional[Member]:
        row = conn.execute("SELECT * FROM members WHERE name = ?", (name,)).fetchone()
        return Member(**dict(row)) if row else None

    def list_all(self, conn: sqlite3.Connection) -> list[Member]:
        rows = conn.execute("SELECT * FROM members ORDER BY name").fetchall()
        return [Member(**dict(r)) for r in rows]

    def delete(self, conn: sqlite3.Connection, member_id: int) -> None:
        conn.execute("DELETE FROM members WHERE id = ?", (member_id,))


# -------------------------------------------------------------------- tasks
class TaskRepository:
    def add(self, conn: sqlite3.Connection, t: Task) -> int:
        cur = conn.execute(
            """INSERT INTO tasks (project_id, assignee_id, title, due_date, importance,
                                  effort, status, created_at, completed_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (t.project_id, t.assignee_id, t.title, t.due_date, t.importance,
             t.effort, t.status, t.created_at, t.completed_at),
        )
        return cur.lastrowid

    def get(self, conn: sqlite3.Connection, task_id: int) -> Optional[Task]:
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return Task(**dict(row)) if row else None

    def update(self, conn: sqlite3.Connection, t: Task) -> None:
        conn.execute(
            """UPDATE tasks SET project_id = ?, assignee_id = ?, title = ?, due_date = ?,
                                importance = ?, effort = ?
               WHERE id = ?""",
            (t.project_id, t.assignee_id, t.title, t.due_date, t.importance, t.effort, t.id),
        )

    def set_status(self, conn: sqlite3.Connection, task_id: int, status: str,
                   completed_at: Optional[str]) -> None:
        conn.execute(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (status, completed_at, task_id),
        )

    def delete(self, conn: sqlite3.Connection, task_id: int) -> None:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

    def list_all(self, conn: sqlite3.Connection) -> list[Task]:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
        return [Task(**dict(r)) for r in rows]

    def list_open(self, conn: sqlite3.Connection) -> list[Task]:
        rows = conn.execute("SELECT * FROM tasks WHERE status <> 'DONE' ORDER BY id").fetchall()
        return [Task(**dict(r)) for r in rows]

    def search(self, conn: sqlite3.Connection, project_id: Optional[int] = None,
               assignee_id: Optional[int] = None, status: Optional[str] = None,
               due_from: Optional[str] = None, due_to: Optional[str] = None,
               text: Optional[str] = None) -> list[Task]:
        """Filters combine with AND. Any filter left as None is ignored."""
        sql = "SELECT * FROM tasks WHERE 1 = 1"
        params: list = []
        if project_id is not None:
            sql += " AND project_id = ?"
            params.append(project_id)
        if assignee_id is not None:
            sql += " AND assignee_id = ?"
            params.append(assignee_id)
        if status is not None:
            sql += " AND status = ?"
            params.append(status)
        if due_from is not None:
            sql += " AND due_date >= ?"
            params.append(due_from)
        if due_to is not None:
            sql += " AND due_date <= ?"
            params.append(due_to)
        if text:
            escaped = text.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            sql += " AND title LIKE ? ESCAPE '\\'"
            params.append(f"%{escaped}%")
        sql += " ORDER BY id"
        return [Task(**dict(r)) for r in conn.execute(sql, params).fetchall()]


# ------------------------------------------------------------- dependencies
class DependencyRepository:
    """Edge 'task_id depends on depends_on_id'. Cycle checks are done in the
    service layer BEFORE calling add()."""

    def add(self, conn: sqlite3.Connection, task_id: int, depends_on_id: int) -> None:
        conn.execute(
            "INSERT INTO task_dependencies (task_id, depends_on_id) VALUES (?, ?)",
            (task_id, depends_on_id),
        )

    def remove(self, conn: sqlite3.Connection, task_id: int, depends_on_id: int) -> None:
        conn.execute(
            "DELETE FROM task_dependencies WHERE task_id = ? AND depends_on_id = ?",
            (task_id, depends_on_id),
        )

    def prerequisites_of(self, conn: sqlite3.Connection, task_id: int) -> list[int]:
        rows = conn.execute(
            "SELECT depends_on_id FROM task_dependencies WHERE task_id = ? ORDER BY depends_on_id",
            (task_id,),
        ).fetchall()
        return [r["depends_on_id"] for r in rows]

    def dependants_of(self, conn: sqlite3.Connection, task_id: int) -> list[int]:
        rows = conn.execute(
            "SELECT task_id FROM task_dependencies WHERE depends_on_id = ? ORDER BY task_id",
            (task_id,),
        ).fetchall()
        return [r["task_id"] for r in rows]

    def all_edges(self, conn: sqlite3.Connection) -> dict[int, list[int]]:
        """Return {task_id: [tasks it depends on]} (the graph for cycle detection)."""
        graph: dict[int, list[int]] = {}
        for r in conn.execute("SELECT task_id, depends_on_id FROM task_dependencies"):
            graph.setdefault(r["task_id"], []).append(r["depends_on_id"])
        return graph

    def open_dependant_counts(self, conn: sqlite3.Connection) -> dict[int, int]:
        """{task_id: number of NOT-DONE tasks that depend on it} (used for factor B)."""
        rows = conn.execute(
            """SELECT d.depends_on_id AS tid, COUNT(*) AS n
               FROM task_dependencies d JOIN tasks t ON t.id = d.task_id
               WHERE t.status <> 'DONE'
               GROUP BY d.depends_on_id"""
        ).fetchall()
        return {r["tid"]: r["n"] for r in rows}

    def blocked_task_ids(self, conn: sqlite3.Connection) -> set[int]:
        """Tasks that have at least one prerequisite that is not DONE."""
        rows = conn.execute(
            """SELECT DISTINCT d.task_id AS tid
               FROM task_dependencies d JOIN tasks p ON p.id = d.depends_on_id
               WHERE p.status <> 'DONE'"""
        ).fetchall()
        return {r["tid"] for r in rows}


# ----------------------------------------------------------- status history
class StatusHistoryRepository:
    def add(self, conn: sqlite3.Connection, h: StatusHistory) -> int:
        cur = conn.execute(
            """INSERT INTO task_status_history (task_id, old_status, new_status, changed_at)
               VALUES (?, ?, ?, ?)""",
            (h.task_id, h.old_status, h.new_status, h.changed_at),
        )
        return cur.lastrowid

    def for_task(self, conn: sqlite3.Connection, task_id: int) -> list[StatusHistory]:
        rows = conn.execute(
            "SELECT * FROM task_status_history WHERE task_id = ? ORDER BY changed_at, id",
            (task_id,),
        ).fetchall()
        return [StatusHistory(**dict(r)) for r in rows]

    def all_ordered(self, conn: sqlite3.Connection,
                    project_id: Optional[int] = None) -> list[sqlite3.Row]:
        """Every history row (optionally for one project), oldest first.
        Used to replay history for the burndown chart."""
        sql = """SELECT h.*, t.project_id AS project_id
                 FROM task_status_history h JOIN tasks t ON t.id = h.task_id"""
        params: list = []
        if project_id is not None:
            sql += " WHERE t.project_id = ?"
            params.append(project_id)
        sql += " ORDER BY h.changed_at, h.id"
        return conn.execute(sql, params).fetchall()


# ----------------------------------------------------------------- settings
class SettingsRepository:
    def get(self, conn: sqlite3.Connection, key: str, default: Optional[str] = None) -> Optional[str]:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default

    def set(self, conn: sqlite3.Connection, key: str, value: str) -> None:
        conn.execute(
            """INSERT INTO settings (key, value) VALUES (?, ?)
               ON CONFLICT(key) DO UPDATE SET value = excluded.value""",
            (key, value),
        )
