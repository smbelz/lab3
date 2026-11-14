from dataclasses import FrozenInstanceError

import pytest

from src.library_catalog.errors import IncorrectEssenceError
from src.library_catalog.models import Book


def base() -> dict[str, object]:
    """Возвращает базовый словарь, на котором будет тестироваться программа."""
    return {"item_id": 1, "title": "Eugene Onegin", "author": "Alexander Pushkin", "category": "Classic", "year": 1833,
            "copies": 1}


def test_create_valid_book():
    """Тест на создание допустимой сущности."""
    book = Book(item_id=1, title="War And Peace", author="Leo Tolstoy", category="Classic", year=1869, copies=10)
    assert book.item_id == 1
    assert book.copies == 10


def test_invalid_item_id():
    """Тест на создание недопустимой сущности. ID должен быть положительным числом."""
    kwargs = base()
    kwargs["item_id"] = 0
    with pytest.raises(IncorrectEssenceError):
        Book(**kwargs)


def test_invalid_item_id_string():
    """Тест на создание недопустимой сущности. ID должен быть числом, не строкой."""
    kwargs = base()
    kwargs["item_id"] = "1"
    with pytest.raises(IncorrectEssenceError):
        Book(**kwargs)


def test_invalid_category_empty():
    """Тест на создание недопустимой сущности. category не должен быть пустым."""
    kwargs = base()
    kwargs["category"] = "   "
    with pytest.raises(IncorrectEssenceError):
        Book(**kwargs)


def test_invalid_title_empty():
    """Тест на создание недопустимой сущности. title не должен быть пустым."""
    kwargs = base()
    kwargs["title"] = "   "
    with pytest.raises(IncorrectEssenceError):
        Book(**kwargs)


def test_invalid_author_empty():
    """Тест на создание недопустимой сущности. author не должен быть пустым."""
    kwargs = base()
    kwargs["author"] = "   "
    with pytest.raises(IncorrectEssenceError):
        Book(**kwargs)


def test_invalid_year_string():
    """Тест на создание недопустимой сущности. year должен быть числом."""
    kwargs = base()
    kwargs["year"] = "1833"
    with pytest.raises(IncorrectEssenceError):
        Book(**kwargs)


def test_invalid_year_future():
    """Тест на создание недопустимой сущности. year не может быть больше текущего года."""
    kwargs = base()
    kwargs["year"] = 2027
    with pytest.raises(IncorrectEssenceError):
        Book(**kwargs)


def test_invalid_copies():
    """Тест на создание недопустимой сущности. copies должен быть больше 0."""
    kwargs = base()
    kwargs["copies"] = 0
    with pytest.raises(IncorrectEssenceError):
        Book(**kwargs)


def test_round_trip():
    """Тест на round trip словаря."""
    book = Book(item_id=1, title="Sherlock Holmes", author="Arthur Conan Doyle", category="Detective", copies=1,
                year=1887)
    assert Book.from_dict(book.to_dict()) == book


def test_missing_field():
    """Тест на создание недопустимой сущности. Не хватает обязательных полей."""
    book = {"item_id": 1, "title": "Anna Karenina"}
    with pytest.raises(IncorrectEssenceError):
        Book.from_dict(book)


def test_ignore_extra_fields():
    """Тест на игнорирование излишних полей."""
    book = Book.from_dict({"item_id": 1, "title": "War And Peace", "author": "Leo Tolstoy", "category": "Classic",
                           "year": 1869, "copies": 10, "genre": "novel"})
    assert book.item_id == 1


def test_book_is_const():
    """Тест на неизменяемость book."""
    book = Book(item_id=1, title="Eugene Onegin", author="Alexander Pushkin", category="Classic", year=1833, copies=1)
    with pytest.raises(FrozenInstanceError):
        book.author = "Leo Tolstoy"
