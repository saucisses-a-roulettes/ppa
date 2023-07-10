import datetime

import edgedb
from collections.abc import Iterable, Callable, Mapping
from typing import Type, TypeVar, Any


_T = TypeVar("_T")

def edgedb_repository(
    keys_path: dict[str, dict[str, Callable[[Any], Any]]],
    find_by_fields: Iterable[str] | None = None,
    # connection_factory: Callable[[], Any] = lambda: edgedb.connect("edgedb://edgedb@localhost:5656"),
    entity_already_exists_exception: Type[Exception] = ValueError,
    entity_not_found_exception: Type[Exception] = ValueError,
):
    def decorator(cls: _T) -> _T:

        class EdgeDbRepository(cls):

            TYPES_MAPPING: Mapping[Type, str] = {
                str: "<str>",
                int: "<int32>",
                float: "<float64>",
                datetime.datetime: "<datetime>",
            }

            def __init__(self, client: edgedb.Client) -> None:
                self._client = client

            def add(self, entity: Any) -> Any:
                for type_name in keys_path:
                    query = """
                    insert %s {
                        #values#
                    }
                    """ % self._type_name

                    values: list[str] = []

                    for key, path in keys_path[type_name].items():
                        value = path(entity)
                        value = (str(value) if type(value) in (dict, list, set, tuple) else f"{self.TYPES_MAPPING.get(type(value), '')}'{value}'")
                        value = f"{key} := {value}"
                        values.append(value)

                    query = query.replace("#values#", ", ".join(values))

                    try:
                        self._client.execute(query)
                    except edgedb.errors.ConstraintViolationError as err:
                        raise entity_already_exists_exception() from err

            def retrieve(self, id_: Any) -> Any:
                for type_name in keys_path:
                    query = """
                        select
                        default::%s
                        {
                            #fields#
                        }
                        filter.id = <uuid>'#id#'
                    """ % type_name

                    query = query.replace("#fields#", ", ".join(keys_path[type_name].keys()))
                    query = query.replace("#id#", str(id_))

                    if (result := self._client.execute(query)) is None:
                        raise entity_not_found_exception()

                    return result

                    # try:
                    #     return self._store[id_]
                    # except KeyError as err:
                    #     raise entity_not_found_exception() from err
                    #
                # def update(self, entity: Any) -> None:
                #     if entity.id not in self._store:
                #         raise entity_not_found_exception()
                #     self._store[entity.id] = entity
                #
                # def delete(self, id_: Any) -> None:
                #     if id_ not in self._store:
                #         raise entity_not_found_exception()
                #     del self._store[id_]
                #
                # def _make_find_by_method(self, field_name: str) -> Any:
                #     def find_by_method(value: Any) -> list[Any]:
                #         return [entity for id_, entity in self._store.items() if getattr(entity, field_name) == value]
                #
                #     return find_by_method


        return EdgeDbRepository

    return decorator

class User:
    def __init__(self, name: str, children: list[str]) -> None:
        self._name = name
        self._children = children


    @property
    def name(self) -> str:
        return self._name

    @property
    def children(self) -> list[str]:
        return self._children

@edgedb_repository(keys_path={"User": {"name": lambda user: user.name, 'children': lambda user: user.children}})
class UserRepository:
    pass


user_repository = UserRepository(edgedb.create_client())
print(user_repository.retrieve("8d2e00a4-1e7d-11ee-84af-bfb1c79caa15"))
# TODO exclusivity constraint