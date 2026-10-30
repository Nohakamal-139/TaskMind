"""Rebuild the demonstration database from scratch with fictional data.

Run from the project root:
    python scripts/seed_data.py

Creates: 4 projects, 4 members, 64 tasks (8 overdue and still open), 14 dependencies
and about 3-5 weeks of status history (needed by the burndown chart).
The first three tasks are the worked example from the project guide
(T1 Write DB schema, T2 Design icons, T3 Fix login crash).
"""
from __future__ import annotations

import random
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.connection import DEFAULT_DB_PATH, get_connection, init_db, transaction  # noqa: E402
from app.database.repositories import (  # noqa: E402
    DependencyRepository, MemberRepository, ProjectRepository,
    SettingsRepository, StatusHistoryRepository, TaskRepository,
)
from app.models import Member, Project, StatusHistory, Task  # noqa: E402

MEMBERS = ["Nadia", "Omar", "Hana", "Youssef"]
PROJECTS = ["Course portal", "Club website", "Mobile app", "Research lab"]
VERBS = ["Write", "Review", "Design", "Fix", "Test", "Plan", "Update", "Document", "Build", "Refactor"]
OBJECTS = ["login page", "report", "database layer", "API docs", "navigation menu",
           "email templates", "search feature", "user guide", "settings screen",
           "backup script", "dashboard", "onboarding flow", "payment form", "logo"]

N_RANDOM_TASKS = 61          # + 3 worked-example tasks = 64
N_OVERDUE_OPEN = 8


def iso_dt(d: date, hour: int = 10) -> str:
    return datetime(d.year, d.month, d.day, hour, 0, 0).isoformat(timespec="seconds")


def seed(db_path=DEFAULT_DB_PATH, today: date | None = None, rng_seed: int = 42) -> None:
    rng = random.Random(rng_seed)
    today = today or date.today()

    path = Path(db_path)
    if str(db_path) != ":memory:" and path.exists():
        path.unlink()                       # rebuild from scratch
    conn = get_connection(db_path)
    init_db(conn)

    projects, members = ProjectRepository(), MemberRepository()
    tasks, deps = TaskRepository(), DependencyRepository()
    history, settings = StatusHistoryRepository(), SettingsRepository()

    with transaction(conn):                 # ONE transaction: all or nothing
        member_ids = [members.add(conn, Member(name=n)) for n in MEMBERS]
        start = (today - timedelta(days=60)).isoformat()
        end = (today + timedelta(days=90)).isoformat()
        project_ids = [projects.add(conn, Project(name=n, start_date=start, due_date=end))
                       for n in PROJECTS]

        # (title, project index, assignee index, due, importance, effort)
        specs = [
            ("Write DB schema", 0, 0, "2026-11-05", 5, 3),     # T1
            ("Design icons", 1, 2, "2026-11-20", 2, 1),        # T2
            ("Fix login crash", 0, 1, "2026-11-01", 4, 2),     # T3
        ]
        task_info = []   # (id, status, created_date, project_id)

        def create(title, p_idx, a_idx, due, imp, eff, status, created: date):
            completed = None
            if status == "DONE":
                lo = created + timedelta(days=2)
                completed_date = lo + timedelta(days=rng.randint(0, max(0, (today - lo).days)))
                completed = iso_dt(completed_date, 16)
            t = Task(project_id=project_ids[p_idx],
                     assignee_id=member_ids[a_idx] if a_idx is not None else None,
                     title=title, due_date=due, importance=imp, effort=eff,
                     status=status, created_at=iso_dt(created), completed_at=completed)
            tid = tasks.add(conn, t)
            # history: creation, then the transitions that led to the final status
            history.add(conn, StatusHistory(task_id=tid, old_status=None,
                                            new_status="TODO", changed_at=t.created_at))
            if status in ("IN_PROGRESS", "DONE"):
                started = created + timedelta(days=1)
                history.add(conn, StatusHistory(task_id=tid, old_status="TODO",
                                                new_status="IN_PROGRESS",
                                                changed_at=iso_dt(started, 11)))
            if status == "DONE":
                history.add(conn, StatusHistory(task_id=tid, old_status="IN_PROGRESS",
                                                new_status="DONE", changed_at=completed))
            task_info.append((tid, status, created, project_ids[p_idx]))
            return tid

        for title, p, a, due, imp, eff in specs:             # worked example: all TODO
            create(title, p, a, due, imp, eff, "TODO", today - timedelta(days=rng.randint(22, 35)))
        # T4 and T5 are TODO tasks that depend on T1 (so T1 blocks 2 open tasks)
        t4 = create("Build task form", 0, 0, (today + timedelta(days=12)).isoformat(), 3, 3,
                    "TODO", today - timedelta(days=25))
        t5 = create("Test database layer", 0, 3, (today + timedelta(days=15)).isoformat(), 3, 2,
                    "TODO", today - timedelta(days=24))

        overdue_slots = set(rng.sample(range(N_RANDOM_TASKS - 2), N_OVERDUE_OPEN))
        for i in range(N_RANDOM_TASKS - 2):
            title = f"{rng.choice(VERBS)} {rng.choice(OBJECTS)}"
            p_idx = rng.randrange(len(PROJECTS))
            a_idx = rng.randrange(len(MEMBERS)) if rng.random() > 0.05 else None
            created = today - timedelta(days=rng.randint(22, 40))
            if i in overdue_slots:
                status = rng.choice(["TODO", "IN_PROGRESS"])
                due = today - timedelta(days=rng.randint(1, 10))
            else:
                status = rng.choices(["TODO", "IN_PROGRESS", "DONE"], weights=[45, 20, 35])[0]
                due = today + timedelta(days=rng.randint(0, 30))
            create(title, p_idx, a_idx, due.isoformat(), rng.randint(1, 5), rng.randint(1, 5),
                   status, created)

        # Dependencies. T4 and T5 depend on T1 (task id 1).
        deps.add(conn, t4, 1)
        deps.add(conn, t5, 1)
        # Others: later task depends on an earlier one (ids only go "backwards" => no cycles).
        status_of = {tid: st for tid, st, _, _ in task_info}
        added, attempts = 2, 0
        while added < 14 and attempts < 2000:
            attempts += 1
            a, b = rng.sample([t[0] for t in task_info], 2)
            task_id, prereq = max(a, b), min(a, b)
            if prereq == 1 or (task_id, prereq) in ((t4, 1), (t5, 1)):
                continue
            # keep the data consistent: a started/finished task must not wait on an unfinished one
            if status_of[task_id] != "TODO" and status_of[prereq] != "DONE":
                continue
            try:
                deps.add(conn, task_id, prereq)
                added += 1
            except Exception:
                continue

        # default scoring settings used by the priority engine
        for key, value in {"weight_urgency": "0.40", "weight_importance": "0.35",
                           "weight_effort": "0.10", "weight_blocking": "0.15",
                           "horizon_days": "14"}.items():
            settings.set(conn, key, value)

    conn.close()
    print(f"Database rebuilt at {db_path}")


if __name__ == "__main__":
    seed()
