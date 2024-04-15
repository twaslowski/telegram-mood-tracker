import pytest

from src.handlers.graphing import get_month_tuples_for_time_range
from src.visualise import Month


@pytest.mark.asyncio
async def test_should_graph_for_correct_months():
    assert [Month(2021, 6)] == get_month_tuples_for_time_range(1, 2021, 6)
    assert [Month(2021, 5), Month(2021, 6)] == get_month_tuples_for_time_range(
        2, 2021, 6
    )
    assert [
        Month(2020, 11),
        Month(2020, 12),
        Month(2021, 1),
    ] == get_month_tuples_for_time_range(3, 2021, 1)
