"""Тесты каталога библоитечных книг."""

import json
from pathlib import Path

import pytest

from src.library_catalog.catalog import LibraryCatalog
from src.library_catalog.errors import (
    DamagedFileError,
    DuplicateIDError,
    ObjectNotFoundError,
    UnsupportedFormatError,
)
from src.library_catalog.models import Book


def make_book(item_id: int = 1, title: str = "Eugene Onegin", author: str = "Alexander Pushkin",
              category: str = "Classic", year: int = 1833, copies: int = 1) -> Book:
    """Создать валидную книгу для тестов."""
    return Book(item_id=item_id, title=title, author=author, category=category, year=year, copies=copies)


def test_add_and_get():
    """Добавление и получение: add сохраняет объект, get возвращает его же."""
    catalog = LibraryCatalog()
    book = make_book()
    catalog.add(book)
    assert catalog.get(1) is book
    assert len(catalog) == 1


def test_remove():
    """Удаление: после remove каталог пуст."""
    catalog = LibraryCatalog()
    book = make_book()
    catalog.add(book)
    catalog.remove(1)
    assert len(catalog) == 0


def test_get_missing_id():
    """Получение отсутствующего."""
    catalog = LibraryCatalog()
    book = make_book()
    catalog.add(book)
    with pytest.raises(ObjectNotFoundError):
        catalog.get(2)


def test_remove_missing_id():
    """Удаление отсутствующего ID."""
    catalog = LibraryCatalog()
    with pytest.raises(ObjectNotFoundError):
        catalog.remove(5)


def test_add_duplicate_id():
    """Добавление уже существующего ID."""
    catalog = LibraryCatalog()
    book = make_book()
    catalog.add(book)
    with pytest.raises(DuplicateIDError):
        catalog.add(book)


def test_find_by_category():
    """Поиск по категории."""
    catalog = LibraryCatalog()
    catalog.add(make_book())
    catalog.add(make_book(item_id=2, category="DETECTIVE"))
    catalog.add(make_book(item_id=3, category="Fiction"))
    catalog.add(make_book(item_id=4, category="classic"))
    catalog.add(make_book(item_id=5, category="CLASSIC"))
    assert [b.item_id for b in catalog.find_by_category("classic")] == [1, 4, 5]


def test_find_by_name():
    """Поиск по имени."""
    catalog = LibraryCatalog()
    catalog.add(make_book())
    catalog.add(make_book(item_id=2, title="Anna Karenina"))
    catalog.add(make_book(item_id=3, title="War And Peace"))
    catalog.add(make_book(item_id=4, title="Harry Potter"))
    catalog.add(make_book(item_id=5, title="ANNA KARENINA"))
    assert [b.item_id for b in catalog.find_by_name("Anna Karenina")] == [2, 5]


def test_json_round_trip(tmp_path: Path):
    """Round trip JSON."""
    catalog = LibraryCatalog()
    catalog.add(make_book(item_id=1))
    catalog.add(make_book(item_id=2))
    path = tmp_path / "catalog.json"
    catalog.save(path)
    loaded = LibraryCatalog.load(path)
    assert len(loaded) == 2
    assert loaded.get(1) == catalog.get(1)


def test_contains():
    """Проверка на содержание."""
    catalog = LibraryCatalog()
    catalog.add(make_book())
    assert 1 in catalog
    assert 2 not in catalog
    assert "1" not in catalog


def test_order_iteration():
    """Порядок итерации детерминирован (по возрастанию item_id)."""
    catalog = LibraryCatalog()
    for i in [3, 2, 1]:
        catalog.add(make_book(item_id=i))
    assert [x.item_id for x in catalog] == [1, 2, 3]


def test_broken_json(tmp_path: Path):
    """Повреждённый JSON."""
    path = tmp_path / "broken.json"
    path.write_text("{ broken json", encoding="utf-8")
    with pytest.raises(DamagedFileError):
        LibraryCatalog.load(path)


def test_unsupported_version(tmp_path: Path):
    """Неизвестная версия формата."""
    path = tmp_path / "unsupported_version.json"
    path.write_text(json.dumps({"format_version": 1000, "items": []}), encoding="utf-8")
    with pytest.raises(UnsupportedFormatError):
        LibraryCatalog.load(path)


def test_load_not_modify_existing(tmp_path: Path):
    """Повреждённый файл не меняет существующий каталог."""
    catalog = LibraryCatalog()
    catalog.add(make_book())
    now = [x.item_id for x in catalog]
    path = tmp_path / "not_modified.json"
    path.write_text(json.dumps({"format_version": 1, "items": [make_book(item_id=2).to_dict(), {"item_id": 3}]}),
                    encoding="utf-8")
    with pytest.raises(DamagedFileError):
        LibraryCatalog.load(path)
    assert [x.item_id for x in catalog] == now


def test_duplicate_in_file(tmp_path: Path):
    """Дубликат в файле."""
    path = tmp_path / "duplicate_in_file.json"
    path.write_text(json.dumps({"format_version": 1, "items": [make_book().to_dict(), make_book().to_dict()]}),
                    encoding="utf-8")
    with pytest.raises(DamagedFileError):
        LibraryCatalog.load(path)


def test_format_version_in_root(tmp_path: Path):
    """format_version в корне документа."""
    catalog = LibraryCatalog()
    catalog.add(make_book())
    path = tmp_path / "catalog.json"
    catalog.save(path)
    file = json.loads(path.read_text(encoding="utf-8"))
    assert "format_version" in file
    assert file["format_version"] == 1
