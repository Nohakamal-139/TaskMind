import sqlite3
from datetime import date

import pytest

from app.database.connection import get_connection, init_db, transaction
from app.database.repositories import (
    DependencyRepository, MemberRepository, ProjectRepository,
    StatusHistoryRepository, TaskRepository,
)
from app.models import Member, Project, StatusHistory, Task
from scripts.seed_data import seed

NOW = "2026-10-26T10:00:00"


def make_project(conn, name="P1"):
    return ProjectRepository().add(conn, Project(name=name, start_date="2026-10-01", due_date="2026-12-31"))


def make_task(conn, project_id, title="Write schema", importance=3, effort=3, **kw):
    return TaskRepository().add(conn, Task(project_id=project_id, title=title, due_date="2026-11-05",
                                           importance=importance, effort=effort, created_at=NOW, **kw))


def test_schema_creates_all_tables(conn):
    names = {r["name"] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"projects", "members", "tasks", "task_dependencies",
            "task_status_history", "settings"} <= names


def test_foreign_keys_are_enabled(conn):
    assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1


def test_importance_and_effort_must_be_1_to_5(conn):
    pid = make_project(conn)
    with pytest.raises(sqlite3.IntegrityError):
        make_task(conn, pid, importance=6)
    with pytest.raises(sqlite3.IntegrityError):
        make_task(conn, pid, effort=0)


def test_invalid_status_and_short_title_rejected(conn):
    pid = make_project(conn)
    with pytest.raises(sqlite3.IntegrityError):
        make_task(conn, pid, status="DOING")
    with pytest.raises(sqlite3.IntegrityError):
        make_task(conn, pid, title="ab")


def test_project_due_date_not_before_start(conn):
    with pytest.raises(sqlite3.IntegrityError):
        ProjectRepository().add(conn, Project(name="Bad", start_date="2026-12-01", due_date="2026-11-01"))


def test_self_dependency_rejected(conn):
    t = make_task(conn, make_project(conn))
    with pytest.raises(sqlite3.IntegrityError):
        DependencyRepository().add(conn, t, t)


def test_duplicate_dependency_rejected_one_row_remains(conn):
    pid = make_project(conn)
    a, b = make_task(conn, pid, "Task A"), make_task(conn, pid, "Task B")
    deps = DependencyRepository()
    deps.add(conn, a, b)
    with pytest.raises(sqlite3.IntegrityError):
        deps.add(conn, a, b)
    assert deps.prerequisites_of(conn, a) == [b]


def test_cannot_delete_project_that_has_tasks(conn):
    pid = make_project(conn)
    make_task(conn, pid)
    with pytest.raises(sqlite3.IntegrityError):
        ProjectRepository().delete(conn, pid)


def test_deleting_member_sets_assignee_to_null(conn):
    pid = make_project(conn)
    mid = MemberRepository().add(conn, Member(name="Nadia"))
    tid = make_task(conn, pid, assignee_id=mid)
    MemberRepository().delete(conn, mid)
    assert TaskRepository().get(conn, tid).assignee_id is None


def test_deleting_task_cascades_to_dependencies_and_history(conn):
    pid = make_project(conn)
    a, b = make_task(conn, pid, "Task A"), make_task(conn, pid, "Task B")
    DependencyRepository().add(conn, a, b)
    StatusHistoryRepository().add(conn, StatusHistory(task_id=a, new_status="TODO", changed_at=NOW))
    TaskRepository().delete(conn, a)
    assert DependencyRepository().prerequisites_of(conn, a) == []
    assert StatusHistoryRepository().for_task(conn, a) == []


def test_task_filters_combine_with_and(conn):
    pid = make_project(conn)
    make_task(conn, pid, "Fix login crash")
    make_task(conn, pid, "Fix icons", status="DONE")
    repo = TaskRepository()
    assert len(repo.search(conn, text="fix")) == 2
    assert [t.title for t in repo.search(conn, text="fix", status="DONE")] == ["Fix icons"]
    assert repo.search(conn, text="nothing-matches") == []


def test_open_dependant_counts_and_blocked(conn):
    pid = make_project(conn)
    t1, t2, t3 = (make_task(conn, pid, f"Task {i}") for i in "123")
    deps = DependencyRepository()
    deps.add(conn, t2, t1)
    deps.add(conn, t3, t1)
    assert deps.open_dependant_counts(conn) == {t1: 2}
    assert deps.blocked_task_ids(conn) == {t2, t3}
    TaskRepository().set_status(conn, t1, "DONE", NOW)
    assert deps.blocked_task_ids(conn) == set()


def test_seed_meets_project_minimums(tmp_path):
    db = tmp_path / "seed.db"
    seed(db, today=date(2026, 10, 26))
    conn = get_connection(db)
    one = lambda sql: conn.execute(sql).fetchone()[0]
    assert one("SELECT COUNT(*) FROM projects") >= 4
    assert one("SELECT COUNT(*) FROM members") >= 4
    assert one("SELECT COUNT(*) FROM tasks") >= 60
    assert one("SELECT COUNT(*) FROM tasks WHERE status <> 'DONE' AND due_date < '2026-10-26'") >= 6
    assert one("SELECT COUNT(*) FROM task_dependencies") >= 10
    span = one("SELECT julianday(MAX(changed_at)) - julianday(MIN(changed_at)) FROM task_status_history")
    assert span >= 21
    # worked example: T1 blocks two open tasks
    assert DependencyRepository().open_dependant_counts(conn)[1] == 2
    conn.close()


def test_t05_duplicate_dependency_after_reconnect(tmp_path):
    """Spec T-05: insert the same dependency twice, reconnect -> one row remains."""
    db = tmp_path / "t05.db"
    c1 = get_connection(db)
    init_db(c1)
    pid = make_project(c1)
    a, b = make_task(c1, pid, "Task A"), make_task(c1, pid, "Task B")
    DependencyRepository().add(c1, a, b)
    c1.commit()
    c1.close()

    c2 = get_connection(db)                       # reconnect
    with pytest.raises(sqlite3.IntegrityError):
        DependencyRepository().add(c2, a, b)
    assert c2.execute("SELECT COUNT(*) FROM task_dependencies").fetchone()[0] == 1
    c2.close()


def test_transaction_rolls_back_everything_on_error(conn):
    pid = make_project(conn)
    conn.commit()
    with pytest.raises(sqlite3.IntegrityError):
        with transaction(conn):
            make_task(conn, pid, "Valid task")        # would be saved...
            make_task(conn, pid, "Bad task", importance=9)   # ...but this fails
    assert conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 0
