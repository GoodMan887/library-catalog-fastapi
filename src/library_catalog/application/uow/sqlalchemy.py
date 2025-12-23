from sqlalchemy.ext.asyncio import AsyncSession

from src.library_catalog.data.repositories.book_repository import BookRepository


class SqlAlchemyUnitOfWork:
    """SQLAlchemy реализация UnitOfWork."""

    def __init__(self, session_factory):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None

    async def __aenter__(self):
        self._session = self._session_factory()

        # ✅ Все репозитории с ОБЩЕЙ сессией
        self.books = BookRepository(self._session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        await self._session.close()

    async def commit(self):
        """✅ ЕДИНСТВЕННОЕ место где делается commit."""
        await self._session.commit()

    async def rollback(self):
        await self._session.rollback()
