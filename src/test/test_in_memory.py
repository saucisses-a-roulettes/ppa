import pytest

from src.in_memory import in_memory_repository


@pytest.fixture
def User():
    class User:
        def __init__(self, id_: int, name: str):
            self.id = id_
            self.name = name

    return User


@pytest.fixture
def UserRepository(User):
    @in_memory_repository
    class UserRepository:
        pass

    return UserRepository()


@pytest.mark.parametrize("entity_id, entity_name", [(1, "John"), (2, "Alice"), (3, "Bob")])
def test_in_memory_behavior(UserRepository, User, entity_id, entity_name):
    user = User(id_=entity_id, name=entity_name)

    UserRepository.add(user)
    retrieved_user = UserRepository.retrieve(entity_id)
    assert retrieved_user == user

    updated_user = User(id_=entity_id, name="Updated Name")
    UserRepository.update(updated_user)
    assert UserRepository.retrieve(entity_id) == updated_user

    UserRepository.delete(entity_id)
    with pytest.raises(ValueError):
        UserRepository.retrieve(entity_id)
