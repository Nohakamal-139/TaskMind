# TaskMind — Intelligent Task Prioritization

TaskMind helps a small team manage projects and tasks and decide what to work on next.
Every open task gets a 0–100 priority score from urgency, importance, effort and how many
other tasks it blocks. Weights are adjustable, each score is broken into its parts, and tasks
waiting on unfinished prerequisites are marked as Blocked.

**Team:** Tnn (replace with the team number) · Project 10, Python GUI Project Catalog 2026

| Member | Name | Primary ownership |
|---|---|---|
| Member 1 | _(Asma)_ | Architecture & database: structure, `schema.sql`, repositories, transactions, seed data, integration |
| Member 2 | _(name)_ | Algorithms & business logic (`algorithms/`, `services/`) |
| Member 3 | _(name)_ | GUI: main window, four screens |
| Member 4 | _(name)_ | Analytics, import/export, tests, packaging |

## Features (status)
| ID | Feature | Status |
|---|---|---|
| FR-01 | Create/edit projects and tasks with validation | Database layer done; service + GUI pending |
| FR-02 | Filters (project, assignee, status, due range, text) | Repository `TaskRepository.search` done; GUI pending |
| FR-03 | Dependencies with cycle rejection | Table + repository done; cycle check pending |
| FR-04 | Status workflow with history | Tables + repository done; service pending |
| FR-05 | Priority Board / "Do next" | Pending |
| FR-06 | Weight sliders (save/reset) | `settings` table ready; GUI pending |
| FR-07 | Progress analytics | History data seeded; charts pending |
| FR-08 | CSV import / export | Sample `data/tasks_import.csv` ready; code pending |

## Requirements
Python 3.11 or 3.12 (everyone on the same minor version). Operating systems tested: _(fill in)_.

## Installation
```bash
git clone <repository-url>
cd <repository-folder>
python -m venv .venv
.venv\Scripts\activate          # Windows  (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
```

## Running
```bash
python scripts/seed_data.py     # rebuilds data/taskmind.db with fictional sample data
python main.py                  # starts the application
```
The database file is not committed to Git; the seed script rebuilds it from scratch at any time.

## Running tests
```bash
pytest
```
Expected: all tests pass (currently 15 database tests).

## Screens
_(screenshots S1–S4 go in `docs/screenshots/` — added later)_

## Algorithm summary
Score = 100 × (wU·U + wI·I + wE·E + wB·B), each factor normalised to 0–1; default weights
0.40 / 0.35 / 0.10 / 0.15. Blocked = any prerequisite not DONE. Cycles are rejected by a
depth-first search before a dependency is saved. Full details: technical documentation (later).

## Database design
ER diagram: `docs/er_diagram.png` (also `docs/er_diagram.md`).
- One connection factory: `app.database.connection.get_connection()` (foreign keys ON).
- Repositories in `app/database/repositories.py` own **all** SQL, with `?` parameters only.
- Repositories never commit; services use `with transaction(conn):` (all-or-nothing).
- Scores are never stored; they are computed on demand.

## Project structure
```
main.py                 starts QApplication
app/ui/                 windows and screens (no SQL)
app/services/           use cases + validation (no SQL)
app/algorithms/         pure Python logic (no Qt, no SQL)
app/models/             dataclasses
app/database/           schema.sql, connection.py, repositories.py
app/utils/              validators, logging
data/                   tasks_import.csv (2 deliberately invalid rows)
scripts/seed_data.py    rebuilds the demo database
tests/                  pytest tests
docs/                   ER diagram, screenshots
```

## Git workflow
`main` always runs. Work on `feature/...` branches, open a Pull Request, get one teammate's
review, then merge. Commit format: `type(scope): summary` (e.g. `feat(m1): add schema`).
Tags at checkpoints: `cp1`, `cp2`, `cp3`, `v1.0`.

## Known limitations
_(updated before submission)_
