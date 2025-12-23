from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..data.repositories.book_repository import BookRepository
from ..data.repositories.protocols import BookRepositoryProtocol
from ..domain.services.book_service import BookService
from ..external.openlibrary.client import OpenLibraryClient
from ..external.protocols import MetadataGatewayProtocol
from ..core.clients import clients_manager


# ========== EXTERNAL CLIENTS (Singletons) ==========

def get_openlibrary_client() -> OpenLibraryClient:
    """
    Получить OpenLibrary клиент из менеджера.

    Клиент создается lazy и переиспользуется между запросами.
    НЕ использует lru_cache для корректного cleanup.
    """
    return clients_manager.get_openlibrary()


# ========== REPOSITORIES ==========

async def get_book_repository(
        db: Annotated[AsyncSession, Depends(get_db)]
) -> BookRepositoryProtocol:
    """
    Создать BookRepository для текущей сессии БД.

    Создается новый экземпляр для каждого запроса.
    """
    return BookRepository(db)


# ========== SERVICES ==========

async def get_book_service(
        book_repo: Annotated[BookRepositoryProtocol, Depends(get_book_repository)],
        ol_client: Annotated[MetadataGatewayProtocol, Depends(get_openlibrary_client)],
) -> BookService:
    """
    Создать BookService с внедренными зависимостями.

    FastAPI автоматически разрешит все зависимости:
    1. get_db() создаст AsyncSession
    2. get_book_repository() создаст BookRepository с session
    3. get_openlibrary_client() вернет singleton клиент
    4. Все внедрится в BookService
    """
    return BookService(
        book_repository=book_repo,
        metadata_gateway=ol_client,
    )


# ========== TYPE ALIASES ДЛЯ УДОБСТВА ==========

# Можно использовать в роутерах так:
# async def my_route(service: BookServiceDep):
BookServiceDep = Annotated[BookService, Depends(get_book_service)]
BookRepoDep = Annotated[BookRepository, Depends(get_book_repository)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
