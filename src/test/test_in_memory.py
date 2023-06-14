from typing import Any

import pytest

from src.in_memory import in_memory_repository


class User:
    def __init__(self, id_: int, name: str):
        self.id = id_
        self.name = name


@pytest.fixture
def user():
    return User(1, "john")


@in_memory_repository(find_by_fields=[])
class UserRepository:
    pass


@pytest.fixture
def user_repository():
    return UserRepository()


def test_in_memory_repository_find_by_fields(user: User):
    @in_memory_repository(find_by_fields=("id", "name"))
    class FieldsRepository:
        pass

    rep: Any = FieldsRepository()

    rep.add(user)

    assert rep.find_by_id(user.id) == [user]
    assert rep.find_by_name(user.name) == [user]


def test_in_memory_repository_exceptions(user: User):
    class CustomException1(Exception):
        pass

    class CustomException2(Exception):
        pass

    @in_memory_repository(
        entity_already_exists_exception=CustomException1,
        entity_not_found_exception=CustomException2,
    )
    class ExceptionsRepository:
        pass

    rep: Any = ExceptionsRepository()

    with pytest.raises(CustomException2):
        rep.delete(user.id)

    rep.add(user)
    with pytest.raises(CustomException1):
        rep.add(user)


def test_in_memory_repository_methods(user_repository: Any, user: User):
    user_repository.add(user)
    assert user_repository.retrieve(user.id) == user
    updated_user = User(id_=user.id, name="john_updated")
    user_repository.update(updated_user)
    modified_user = user_repository.retrieve(user.id)
    assert modified_user.id == updated_user.id and modified_user.name == updated_user.name
    user_repository.delete(user.id)
    with pytest.raises(ValueError):
        assert user_repository.retrieve(user.id)


def test_in_memory_repository_add_already_exists(user_repository: Any, user: User):
    user_repository.add(user)
    with pytest.raises(ValueError):
        user_repository.add(user)


def test_in_memory_repository_update_not_found(user_repository: Any, user: User):
    with pytest.raises(ValueError):
        user_repository.update(user)


def test_in_memory_repository_delete_not_found(user_repository: Any, user: User):
    with pytest.raises(ValueError):
        user_repository.delete(user)
