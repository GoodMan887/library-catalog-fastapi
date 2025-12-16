from src.library_catalog.data.models.book import Book
from src.library_catalog.data.repositories.base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List, Any


class BookRepository(BaseRepository[Book]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Book)

    def _build_filter_clauses(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None
    ) -> List[Any]:
        """Вспомогательный метод для построения условий WHERE."""
        filters = []
        model = self.model

        if title:
            filters.append(model.title.ilike(f"%{title}%"))
        if author:
            filters.append(model.author.ilike(f"%{author}%"))
        if genre:
            filters.append(model.genre.ilike(f"%{genre}%"))
        if year is not None:
            filters.append(model.year == year)
        if available is not None:
            filters.append(model.available == available)

        return filters

    async def find_by_filters(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
            limit: int = 20,
            offset: int = 0,
    ) -> list[Book]:
        """Поиск книг с фильтрацией и пагинацией."""
        filters = self._build_filter_clauses(title, author, genre, year, available)

        request = (
            select(self.model)
            .where(and_(*filters))
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(request)
        return list(result.scalars().all())

    async def find_by_isbn(self, isbn: str) -> Book | None:
        """Найти книгу по ISBN."""
        request = select(self.model).where(self.model.isbn == isbn)

        result = await self.session.execute(request)
        return result.scalars().first()

    async def count_by_filters(
            self,
            title: str | None = None,
            author: str | None = None,
            genre: str | None = None,
            year: int | None = None,
            available: bool | None = None,
    ) -> int:
        """Подсчитать количество книг по фильтрам."""
        filters = self._build_filter_clauses(title, author, genre, year, available)

        request = select(func.count()).where(and_(*filters)).select_from(self.model)

        result = await self.session.execute(request)
        return result.scalar_one()
