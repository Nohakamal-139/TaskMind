from app.algorithms.cycle_detector import create, detect_cycle
def test_no_cycle_in_linear_chain():
    deps = {
        1: [2],
        2: [3],
        3: []
    }
    assert create(4, 1, deps) is False
def test_detects_cycle_and_returns_path():
    deps = {
        1: [4],
        4: [2],
        2: []
    }
    assert create(2, 1, deps) is True
    path = detect_cycle(2, 1, deps)
    assert path == [2, 1, 4, 2]
def test_self_dependency_creates_cycle():
    deps = {1: []}
    assert create(1, 1, deps) is True