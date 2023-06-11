import pytest

from ppa.in_memory import in_memory_repository


@pytest.fixture
def User():
    class User:
        def __init__(self, id_: int, name: str):
            self.id = id_
            self.name = name

    return User


@pytest.fixture
def user_repository():
    @in_memory_repository()
    class UserRepository:
        pass

    return UserRepository()


def test_in_memory_repository(user_repository, User):
    user = User(id_=1, name="John")

    user_repository.add(user)
    retrieved_user = user_repository.retrieve(1)
    assert retrieved_user == user

    updated_user = User(id_=1, name="Johny")
    user_repository.update(updated_user)
    assert user_repository.retrieve(1) == updated_user

    user_repository.delete(1)
    with pytest.raises(ValueError):
        user_repository.retrieve(1)
