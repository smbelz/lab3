"""Исключения каталога."""


class CatalogError(Exception):
    """Базовое исключение каталога."""


class IncorrectEssenceError(CatalogError):
    """Ошибка неверной сущности."""


class DuplicateIDError(CatalogError):
    """Ошибка дублирования ID."""


class ObjectNotFoundError(CatalogError):
    """Объект с данным ID не найден."""


class UnsupportedFormatError(CatalogError):
    """Ошибка неподдерживаемой версии формата."""


class DamagedFileError(CatalogError):
    """Файл повреждён."""
