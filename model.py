import datetime
from dataclasses import dataclass
from typing import List, Optional, Set


class AllocationException(Exception):
    """Represents any problems with goods allocation."""


@dataclass(frozen=True)
class OrderLine:
    """Models order line."""

    order_reference: str
    item: str
    quantity: int


class Batch:
    """Models a batch"""

    def __init__(
        self, batch_id: str, item: str, quantity: int, eta: Optional[datetime.date]
    ):
        self.batch_id = batch_id
        self.item = item
        self.eta = eta
        self._initial_quantity = quantity
        self._allocations: Set[OrderLine] = set()

    def allocate(self, line: OrderLine) -> None:
        if not self.can_allocate(line):
            raise AllocationException("Cannot allocate line.")
        if line.order_reference not in self._allocations:
            self._allocations.add(line)

    def can_allocate(self, line: OrderLine) -> bool:
        return (
            self.item == line.item
            and self.available_quantity >= line.quantity
            and line.quantity > 0
        )

    def deallocate(self, line: OrderLine) -> None:
        if line in self._allocations:
            self._allocations.remove(line)

    @property
    def available_quantity(self) -> int:
        return self._initial_quantity - sum([a.quantity for a in self._allocations])

    def __lt__(self, other: "Batch") -> bool:
        if self.eta is None:
            return True
        if other.eta is None:
            return False
        return self.eta < other.eta


class OutOfStock(Exception):
    pass


def allocate(line: OrderLine, batches: List[Batch]) -> Optional[str]:
    for batch in sorted(batches):
        if batch.can_allocate(line):
            batch.allocate(line)
            return batch.batch_id
    raise OutOfStock(f"SKU {line.item} is out of stock.")
