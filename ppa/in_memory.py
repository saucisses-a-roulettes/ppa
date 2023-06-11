from typing import Any, Type


def in_memory_repository(
    entity_already_exists_exception: Type[Exception] = ValueError,
    entity_not_found_exception: Type[Exception] = ValueError,
):
    def decorator(cls) -> Type:
        e_already_exists = entity_already_exists_exception
        e_not_found = entity_not_found_exception

        class InMemoryRepository(cls):
            find_by_fields: list[str] = ["id"]
            entity_already_exists_exception: Type[Exception] = e_already_exists
            entity_not_found_exception: Type[Exception] = e_not_found

            def __init__(self) -> None:
                self._store: dict[str, Any] = {}
                for key in self.find_by_fields:
                    setattr(self, f"find_by_{key}", self._make_find_by_method(key))

            def add(self, entity: Any) -> Any:
                if entity.id in self._store:
                    raise self.entity_already_exists_exception()
                self._store[entity.id] = entity

            def retrieve(self, id_: Any) -> Any:
                try:
                    return self._store[id_]
                except KeyError as err:
                    raise self.entity_not_found_exception() from err

            def update(self, entity: Any) -> None:
                if entity.id not in self._store:
                    raise self.entity_not_found_exception()
                self._store[entity.id] = entity

            def delete(self, id_: Any) -> None:
                if id_ not in self._store:
                    raise self.entity_not_found_exception(id_)
                del self._store[id_]

            def _make_find_by_method(self, field_name: str) -> Any:
                def find_by_method(value: Any) -> list[Any]:
                    return [entity for id_, entity in self._store.items() if getattr(entity, field_name) == value]

                return find_by_method

        return InMemoryRepository

    return decorator
