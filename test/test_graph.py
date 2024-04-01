import pytest

from src.handlers.graphing import get_all_months_for_offset


@pytest.mark.asyncio
async def test_should_graph_for_correct_months():
    assert [(2021, 6)] == get_all_months_for_offset(1, 2021, 6)
    assert [(2021, 5), (2021, 6)] == get_all_months_for_offset(2, 2021, 6)
    assert [(2020, 11), (2020, 12), (2021, 1)] == get_all_months_for_offset(3, 2021, 1)
