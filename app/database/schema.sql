-- TaskMind database schema (SQLite)
-- Scores are NOT stored: they are computed on demand from current data.

CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL UNIQUE,
    start_date  TEXT NOT NULL,
    due_date    TEXT NOT NULL,
    CHECK (due_date >= start_date)
);

CREATE TABLE IF NOT EXISTS members (
    id    INTEGER PRIMARY KEY AUTOINCREMENT,
    name  TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS tasks (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id    INTEGER NOT NULL
                  REFERENCES projects(id) ON DELETE RESTRICT,
    assignee_id   INTEGER
                  REFERENCES members(id) ON DELETE SET NULL,
    title         TEXT NOT NULL CHECK (length(title) BETWEEN 3 AND 100),
    due_date      TEXT NOT NULL,
    importance    INTEGER NOT NULL CHECK (importance BETWEEN 1 AND 5),
    effort        INTEGER NOT NULL CHECK (effort BETWEEN 1 AND 5),
    status        TEXT NOT NULL DEFAULT 'TODO'
                  CHECK (status IN ('TODO', 'IN_PROGRESS', 'DONE')),
    created_at    TEXT NOT NULL,
    completed_at  TEXT
);

CREATE TABLE IF NOT EXISTS task_dependencies (
    task_id        INTEGER NOT NULL
                   REFERENCES tasks(id) ON DELETE CASCADE,
    depends_on_id  INTEGER NOT NULL
                   REFERENCES tasks(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, depends_on_id),
    CHECK (task_id <> depends_on_id)
);

CREATE TABLE IF NOT EXISTS task_status_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id     INTEGER NOT NULL
                REFERENCES tasks(id) ON DELETE CASCADE,
    old_status  TEXT,
    new_status  TEXT NOT NULL
                CHECK (new_status IN ('TODO', 'IN_PROGRESS', 'DONE')),
    changed_at  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_tasks_project  ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status   ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_deps_depends   ON task_dependencies(depends_on_id);
CREATE INDEX IF NOT EXISTS idx_history_task   ON task_status_history(task_id);
