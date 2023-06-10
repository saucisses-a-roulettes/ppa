from __future__ import annotations
import dataclasses
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import Annotated, Generic, TypeVar, Protocol, ClassVar, Dict, Any, Type, Self

from pydantic import BaseModel

_TId = TypeVar("_TId")


class _Entity(Protocol):

    @property
    @abstractmethod
    def id(self) -> _TId:
        pass


_TEntity = TypeVar("_TEntity")



class InMemoryRepositoryMetaclass(type):

    # def __init__(self, model: Type[BaseModel]) -> None:
    #     self._model = model
    #     self._store: dict[_TId, _TEntity] = {}
    #     self._create_find_by_methods()

    def __new__(cls: Type[InMemoryRepositoryMetaclass], name: str, bases: tuple, class_dict: dict[str, Any]) -> InMemoryRepositoryMetaclass:
        result = super().__new__(cls, name, bases, class_dict)
        if fields := class_dict.get("find_by_fields"):
            for key in fields:
                setattr(result, f'find_by_{key}', cls._make_find_by_method(key))

        if e := class_dict.get("entity_already_exists_exception"):
            setattr(result, 'add', cls._make_add_method(e))
        if e := class_dict.get("entity_not_found_exception"):
            setattr(result, 'retrieve', cls._make_retrieve_method(e))
            setattr(result, 'update', cls._make_update_method(e))

        return result

    @staticmethod
    def _make_find_by_method(field_name: str) -> Any:
        def find_by_method(self, value: Any) -> list[Any]:
            return [entity for id_, entity in self._store.items() if getattr(entity, field_name) == value]

        return find_by_method

    @staticmethod
    def _make_add_method(entity_already_exists_exception: Type[Exception]) -> Any:
        def add_method(self, entity: Any) -> Any:
            if entity.id in self._store:
                raise entity_already_exists_exception()
            self._store[entity.id] = entity

        return add_method

    @staticmethod
    def _make_retrieve_method(entity_not_found_exception: Type[Exception]) -> Any:
        def retrieve_method(self, id_: Any) -> Any:
            try:
                return self._store[id_]
            except KeyError as err:
                raise entity_not_found_exception() from err
        return retrieve_method

    @staticmethod
    def _make_update_method(entity_not_found_exception: Type[Exception]) -> Any:
        def update_method(self, entity: Any) -> None:
            if entity.id not in self._store:
                raise entity_not_found_exception()
            self._store[entity.id] = entity

        return update_method





    # def delete(self, id_: Id) -> None:
    #     if id_ not in self._store:
    #         raise CannotRetrieveEntity(id_)
    #     del self._store[id_]
    #
    # def all(self) -> List[TEntity]:
    #     return list(self._store.values())


class InMemoryRepository(metaclass=InMemoryRepositoryMetaclass):
    find_by_fields: list[str] = ["id"]
    entity_already_exists_exception: Type[Exception] = ValueError
    entity_not_found_exception: Type[Exception] = ValueError

    def __init__(self) -> None:
        self._test = "test"
        self._store = {}


class Test:

    @property
    def id(self) -> int:
        return 1


rep = InMemoryRepository()

rep.add(Test())
print(rep.find_by_id(1)[0].id)
rep.update(Test())
print(rep.retrieve(1).id)