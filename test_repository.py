from sqlalchemy.orm import Session

import model
import repository


def test_repository_can_save_a_batch(session):
    batch = model.Batch("batch1", "RUSTY-SOAPDISH", 100, eta=None)

    repo = repository.SqlAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = list(session.execute("SELECT reference, sku, _purchased_quantity, eta FROM batches"))
    assert rows == [("batch1", "RUSTY-SOAPDISH", 100, None)]


def insert_order_line(session: Session) -> int:
    session.execute(
        """
    INSERT INTO order_lines (orderid, sku, qty)
    VALUES ("order1", "GENERIC-SOFA", 12)
    """
    )
    [[orderline_id]] = session.execute(
        "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku", dict(orderid="order1", sku="GENERIC-SOFA")
    )
    return orderline_id


def insert_batch(session: Session, batch_id: str) -> int:
    session.execute(
        """
        INSERT INTO batches (reference, sku, _purchased_quantity)
        VALUES (:batch_id, "GENERIC-SOFA", 100)
        """,
        dict(batch_id=batch_id),
    )
    [[batches_id]] = session.execute("SELECT id FROM batches WHERE reference=:batch_id", dict(batch_id=batch_id))

    return batches_id


def insert_allocation(session: Session, orderline_id: int, batch_id: int):
    session.execute(
        """
        INSERT INTO allocations (batch_id, orderline_id)
        VALUES (:batch_id, :orderline_id)
        """,
        dict(batch_id=batch_id, orderline_id=orderline_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")

    insert_allocation(session, orderline_id, batch1_id)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "GENERIC-SOFA", 100, eta=None)

    assert retrieved == expected
