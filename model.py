from dataclasses import dataclass
from datetime import date
from typing import Any, List, Optional, Set


@dataclass(frozen=True)
class OrderLine:
    order_id: str
    sku: str
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]):
        self.reference = ref
        self.sku = sku
        self.eta = eta
        self._purchased_quantity = qty
        self._allocated_lines: Set[OrderLine] = set()

    def allocate(self, line: OrderLine) -> None:
        if self.can_allocate(line):
            self._allocated_lines.add(line)

    def deallocate(self, line: OrderLine):
        if line in self._allocated_lines:
            self._allocated_lines.remove(line)

    @property
    def allocated_quantity(self):
        return sum(line.qty for line in self._allocated_lines)

    @property
    def available_quantity(self) -> int:
        return self._purchased_quantity - self.allocated_quantity

    def can_allocate(self, line: OrderLine) -> bool:
        return line.sku == self.sku and self.available_quantity >= line.qty

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, Batch) or self.eta is None:
            return False
        if other.eta is None:
            return True
        return self.eta > other.eta

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Batch):
            return self.reference == other.reference
        return False

    def __hash__(self):
        return hash(self.reference)


def allocate(line: OrderLine, batches: List[Batch]) -> Optional[str]:
    for batch in sorted(batches):
        if batch.can_allocate(line):
            batch.allocate(line)
            return batch.reference
    raise OutOfStock(f"Product {line.sku} is out of stock.")


class OutOfStock(Exception):
    pass
