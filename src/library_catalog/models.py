"""Предметная модель: библиотечная книга.
Требования:
* использование @dataclass для сущности;
* поля сущности: item_id, title, category, year, author, copies
  (author, copies — поля варианта);
* инварианты проверяются при создании, неверный объект не создаётся;
* to_dict / from_dict для сериализации в JSON;
* frozen=True: объект неизменяем после создания.
"""

from collections.abc import Mapping
from dataclasses import dataclass

from src.library_catalog.errors import IncorrectEssenceError


@dataclass(frozen=True)
class Book:
    item_id: int
    title: str
    category: str
    year: int
    author: str
    copies: int

    def __post_init__(self) -> None:
        errors: list[str] = []
        if not isinstance(self.item_id, int):
            errors.append("item_id должен быть числом")
        elif self.item_id <= 0:
            errors.append("item_id должен быть положительным числом")
        if not isinstance(self.title, str):
            errors.append("title должен быть строкой")
        elif not self.title.strip():
            errors.append("title должен быть непустой строкой")
        if not isinstance(self.category, str):
            errors.append("category должен быть строкой")
        elif not self.category.strip():
            errors.append("category должен быть непустой строкой")
        if not isinstance(self.author, str):
            errors.append("author должен быть строкой")
        elif not self.author.strip():
            errors.append("author должен быть непустой строкой")
        if not isinstance(self.year, int):
            errors.append("year должен быть числом")
        elif self.year > 2026:
            errors.append("year должен быть меньше 2027")
        if not isinstance(self.copies, int):
            errors.append("copies должен быть числом")
        elif self.copies <= 0:
            errors.append("copies должен быть положительным числом")
        if errors:
            raise IncorrectEssenceError(", ".join(errors))

    def to_dict(self) -> dict[str, object]:
        return {
            "item_id": self.item_id,
            "title": self.title,
            "category": self.category,
            "year": self.year,
            "author": self.author,
            "copies": self.copies,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]):
        if not isinstance(data, Mapping):
            raise IncorrectEssenceError("данные о книге должны быть словарём")
        required_fields = ["item_id", "title", "category", "year", "author", "copies"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            raise IncorrectEssenceError(f"Отсутствуют поля {missing_fields}")
        return cls(
            item_id=data["item_id"],
            title=data["title"],
            category=data["category"],
            year=data["year"],
            author=data["author"],
            copies=data["copies"],
        )
