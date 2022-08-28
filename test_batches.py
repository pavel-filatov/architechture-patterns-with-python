import datetime
from typing import Tuple

import pytest

from model import Batch, OrderLine, OutOfStock, allocate

today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)
day_after_tomorrow = today + datetime.timedelta(days=2)


def create_batch_line(
    sku: str, batch_qty: int, line_qty: int
) -> Tuple[Batch, OrderLine]:
    batch = Batch("batch-001", sku, batch_qty, today)
    line = OrderLine("ref-001", sku, line_qty)
    return batch, line


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch, line = create_batch_line("RED-CHAIR", 10, 2)

    batch.allocate(line)

    assert batch.available_quantity == 8


def test_allocating_is_prohibited_if_batch_contains_less_than_asked():
    batch, line = create_batch_line("RED-CHAIR", 10, 20)

    with pytest.raises(OutOfStock):
        allocate(line, [batch])


def test_can_allocate_if_required_quantity_is_smaller_that_available():
    big_batch, small_line = create_batch_line("RED-CHAIR", 20, 1)
    assert big_batch.can_allocate(small_line)


def test_can_allocate_if_required_quantity_equals_available():
    batch, line = create_batch_line("STONE-STOOL", 10, 10)
    assert batch.can_allocate(line)


def test_cannot_allocate_if_required_is_greater_than_available():
    batch, line = create_batch_line("STONE-STOOL", 10, 11)
    assert not batch.can_allocate(line)


def test_cannot_allocate_negative_number():
    batch, line = create_batch_line("RED-CHAIR", 20, -1)
    assert not batch.can_allocate(line)


def test_cannot_allocate_if_skus_are_different():
    batch = Batch(
        batch_id="batch001", item="RED-CHAIR", quantity=10, eta=datetime.datetime.now()
    )
    line = OrderLine("order-ref", "ANOTHER-SKU", 1)

    assert not batch.can_allocate(line)


def test_allocation_is_idempotent():
    batch, line = create_batch_line("BLUE-CHAIR", 10, 2)
    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 8


def test_deallocation_doesnt_work_if_line_want_allocated():
    batch, line = create_batch_line("BLUE-CHAIR", 10, 2)
    batch.deallocate(line)
    assert batch.available_quantity == 10


def test_deallocation_returns_allocated_quantity():
    batch, line = create_batch_line("YELLOW-TABLE", 10, 2)

    batch.allocate(line)
    assert batch.available_quantity == 8

    batch.deallocate(line)
    assert batch.available_quantity == 10


def test_prefers_in_stock_goods():
    in_stock = Batch("batch-001", "SIMPLE-STOOL", 20, None)
    arrives_today = Batch("batch-002", "SIMPLE-STOOL", 20, today)

    line = OrderLine("ref-001", "SIMPLE-STOOL", 10)

    allocate(line, [in_stock, arrives_today])

    assert in_stock.available_quantity == 10
    assert arrives_today.available_quantity == 20


def test_prefers_earlier_delivery():
    arrives_today = Batch("batch-001", "SIMPLE-STOOL", 20, today)
    arrives_tomorrow = Batch("batch-002", "SIMPLE-STOOL", 20, tomorrow)
    arrives_the_day_after_tomorrow = Batch(
        "batch-003", "SIMPLE-STOOL", 20, day_after_tomorrow
    )

    line = OrderLine("ref-001", "SIMPLE-STOOL", 10)

    allocate(line, [arrives_the_day_after_tomorrow, arrives_tomorrow, arrives_today])

    assert arrives_today.available_quantity == 10
    assert arrives_tomorrow.available_quantity == 20
    assert arrives_the_day_after_tomorrow.available_quantity == 20


def test_allocation_precedence():
    in_stock = Batch("batch-001", "SIMPLE-STOOL", 5, None)
    arrives_today = Batch("batch-002", "SIMPLE-STOOL", 20, today)
    arrives_tomorrow = Batch("batch-003", "SIMPLE-STOOL", 10, tomorrow)

    bigger_line = OrderLine("ref-001", "SIMPLE-STOOL", 10)
    smaller_line = OrderLine("ref-002", "SIMPLE-STOOL", 5)

    allocate(bigger_line, [arrives_tomorrow, arrives_today, in_stock])
    allocate(smaller_line, [arrives_tomorrow, arrives_today, in_stock])

    assert in_stock.available_quantity == 0
    assert arrives_today.available_quantity == 10
    assert arrives_tomorrow.available_quantity == 10


def test_allocate_returns_batch_ref():
    in_stock = Batch("batch-001", "SIMPLE-STOOL", 5, None)
    arrives_today = Batch("batch-002", "SIMPLE-STOOL", 20, today)
    arrives_tomorrow = Batch("batch-003", "SIMPLE-STOOL", 10, tomorrow)

    line = OrderLine("ref-001", "SIMPLE-STOOL", 15)

    batch_ref = allocate(line, [in_stock, arrives_today, arrives_tomorrow])

    assert batch_ref == arrives_today.batch_id
