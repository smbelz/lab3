"""Каталог библиотечных книг."""

import json
from collections.abc import Iterator
from pathlib import Path
from src.library_catalog.errors import DamagedFileError, DuplicateIDError, ObjectNotFoundError, UnsupportedFormatError
from src.library_catalog.models import Book


class LibraryCatalog:
    """Каталог книг."""
    VERSION = 1

    def __init__(self) -> None:
        self._items: dict[int, Book] = {}

    def add(self, item: Book) -> None:
        if not isinstance(item, Book):
            raise TypeError("Ожидается Book.")
        if item.item_id in self._items:
            raise DuplicateIDError(f"ID {item.item_id} уже был.")
        self._items[item.item_id] = item

    def get(self, item_id: int) -> Book:
        try:
            return self._items[item_id]
        except KeyError:
            raise ObjectNotFoundError(f"ID {item_id} не найден.")

    def remove(self, item_id: int) -> None:
        if item_id not in self._items:
            raise ObjectNotFoundError(f"ID {item_id} не найден.")
        del self._items[item_id]

    def find_by_category(self, category: str) -> list[Book]:
        if not isinstance(category, str):
            return []
        category = category.strip().lower()
        if not category:
            return []
        return [b for b in self._sorted_items() if b.category.lower() == category]

    def find_by_name(self, query: str) -> list[Book]:
        if not isinstance(query, str):
            return []
        query = query.strip().lower()
        if not query:
            return []
        return [b for b in self._sorted_items() if query == b.title.lower()]

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[Book]:
        return iter(self._sorted_items())

    def __contains__(self, item_id: object) -> bool:
        return isinstance(item_id, int) and item_id in self._items

    def _sorted_items(self) -> list[Book]:
        return [self._items[key] for key in sorted(self._items)]

    def to_json(self) -> dict[str, object]:
        return {
            "format_version": self.VERSION,
            "items": [book.to_dict() for book in self._sorted_items()],
        }

    def save(self, path: str | Path) -> None:
        """Запись в JSON-файл."""
        path = Path(path)
        text = json.dumps(self.to_json(), ensure_ascii=False, indent=2)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    @classmethod
    def load(cls, path: str | Path):
        """Загрузка каталога из JSON."""
        path = Path(path)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except OSError:
            raise DamagedFileError("Не удалось прочитать файл.")
        except json.JSONDecodeError:
            raise DamagedFileError("Некорректный JSON.")

        if not isinstance(data, dict):
            raise DamagedFileError("Корневой элемент должен быть объектом.")
        version = data.get("format_version")
        if not isinstance(version, int):
            raise DamagedFileError("format_version должен быть числом.")
        if version != cls.VERSION:
            raise UnsupportedFormatError("Версия не поддерживается.")
        items_data = data.get("items")
        if not isinstance(items_data, list):
            raise DamagedFileError("items должно быть списком.")
        new_catalog = cls()
        try:
            for entry in items_data:
                book = Book.from_dict(entry)
                if book.item_id in new_catalog._items:
                    raise DamagedFileError(f"Дубликат ID {book.item_id}.")
                new_catalog._items[book.item_id] = book
        except DamagedFileError:
            raise
        except Exception:
            raise DamagedFileError
        return new_catalog
