import pytest
from types import SimpleNamespace
from app.routers.reports import _compute_metrics

class FakeQ:
    def __init__(self, rows):
        self._rows = rows
    def count(self): return len(self._rows)
    def all(self): return self._rows
    def order_by(self, *a, **k): return self

class FakeDB:
    def __init__(self, rows):
        self._rows = rows
    def query(self, *cols):
        # Expect columns (operation, created_at)
        return FakeQ([(r.operation, r.created_at) for r in self._rows])

def test_compute_metrics_basic():
    from datetime import datetime, timedelta
    base = datetime(2025, 1, 1, 12, 0, 0)
    rows = [
        SimpleNamespace(operation="add", created_at=base),
        SimpleNamespace(operation="add", created_at=base + timedelta(seconds=10)),
        SimpleNamespace(operation="mul", created_at=base + timedelta(seconds=25)),
    ]
    m = _compute_metrics(FakeDB(rows))  # type: ignore
    assert m.total_calculations == 3
    assert m.operations_breakdown["add"] == 2
    assert m.operations_breakdown["mul"] == 1
    assert m.first_calculation_at == rows[0].created_at
    assert m.last_calculation_at == rows[-1].created_at
    # avg gap = (25 sec over 2 intervals) = 12.5
    assert abs(m.average_time_between_seconds - 12.5) < 1e-6
