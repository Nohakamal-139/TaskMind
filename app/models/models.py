"""Plain dataclasses that mirror the database tables."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Project:
    name: str
    start_date: str          # "YYYY-MM-DD"
    due_date: str            # "YYYY-MM-DD"
    id: Optional[int] = None


@dataclass
class Member:
    name: str
    id: Optional[int] = None


@dataclass
class Task:
    project_id: int
    title: str
    due_date: str            # "YYYY-MM-DD"
    importance: int          # 1..5
    effort: int              # 1..5
    created_at: str          # ISO datetime
    assignee_id: Optional[int] = None
    status: str = "TODO"     # TODO | IN_PROGRESS | DONE
    completed_at: Optional[str] = None
    id: Optional[int] = None


@dataclass
class StatusHistory:
    task_id: int
    new_status: str
    changed_at: str
    old_status: Optional[str] = None
    id: Optional[int] = None
