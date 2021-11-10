import abc

from sqlalchemy.orm import Session

import model


class AbstractRepository(abc.ABC):
    def add(self, batch: model.Batch):
        raise NotImplementedError

    def get(self, reference: str) -> model.Batch:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session):
        self.__session = session

    def get(self, reference: str) -> model.Batch:
        return self.__session.query(model.Batch).filter_by(reference=reference).one()

    def add(self, batch):
        self.__session.add(batch)
