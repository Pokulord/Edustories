from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    items: list[T]
    total_count: int
    page: int
    page_size: int

    @property
    def total_pages_count(self) -> int:
        """Считает общее количество страниц"""
        if self.page == 0:
            return 0
        # Считаем, сколько страниц нужно
        return (self.total_count + self.page_size - 1) // self.page_size
    
    @property
    def has_next(self) -> bool:
        """Проверяет, есть ли ещё страницы"""
        return self.page < self.total_pages_count

    @property
    def has_previous(self) -> bool:
        """Проверяет, есть ли предшествующие страницы
        (а начиая со второй они точно есть)
        """
        return self.page > 1