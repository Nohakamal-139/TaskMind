from datetime import date
import pytest
from app.algorithms.priority_engine import (
    Weights,
    calc_task_score,
    normalize_weights,
)


def test_worked_example_from_spec():
    today = date(2026, 11, 2)

    score_t1, _ = calc_task_score(
        due_date=date(2026, 11, 5),
        importance=5,
        effort=3,
        open_dep_count=2,
        today=today,
    )
    assert score_t1 == 81.43

    score_t3, _ = calc_task_score(
        due_date=date(2026, 11, 1),
        importance=4,
        effort=2,
        open_dep_count=0,
        today=today,
    )
    assert score_t3 == 73.75

    score_t2, _ = calc_task_score(
        due_date=date(2026, 11, 20),
        importance=2,
        effort=1,
        open_dep_count=0,
        today=today,
    )
    assert score_t2 == 18.75

    assert score_t1 > score_t3 > score_t2


def test_urgency_boundaries():
    
    today = date(2026, 11, 2)

    _, b_today = calc_task_score(
        due_date=today,
        importance=3,
        effort=3,
        open_dep_count=0,
        today=today,
    )
    assert b_today.urgency == 1.0

    _, b_future = calc_task_score(
        due_date=date(2026, 11, 16),
        importance=3,
        effort=3,
        open_dep_count=0,
        today=today,
    )
    assert b_future.urgency == 0.0


def test_normalize_weights():
    w = normalize_weights(40.0, 35.0, 10.0, 35.0)
    total = w.u + w.i + w.e + w.b
    assert round(total, 4) == 1.0