from collections.abc import Iterable
from typing import Any, Type


def in_memory_repository(
    find_by_fields: Iterable[str] | None = None,
    entity_already_exists_exception: Type[Exception] = ValueError,
    entity_not_found_exception: Type[Exception] = ValueError,
):
    if find_by_fields is None:
        find_by_fields = []
    def decorator(cls) -> Type:
        class InMemoryRepository(cls):
            def __init__(self) -> None:
                self._store: dict[str, Any] = {}
                for key in find_by_fields:
                    setattr(self, f"find_by_{key}", self._make_find_by_method(key))

            def add(self, entity: Any) -> Any:
                if entity.id in self._store:
                    raise entity_already_exists_exception()
                self._store[entity.id] = entity

            def retrieve(self, id_: Any) -> Any:
                try:
                    return self._store[id_]
                except KeyError as err:
                    raise entity_not_found_exception() from err

            def update(self, entity: Any) -> None:
                if entity.id not in self._store:
                    raise entity_not_found_exception()
                self._store[entity.id] = entity

            def delete(self, id_: Any) -> None:
                if id_ not in self._store:
                    raise entity_not_found_exception()
                del self._store[id_]

            def _make_find_by_method(self, field_name: str) -> Any:
                def find_by_method(value: Any) -> list[Any]:
                    return [entity for id_, entity in self._store.items() if getattr(entity, field_name) == value]

                return find_by_method

        return InMemoryRepository

    return decorator
