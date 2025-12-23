from typing import Protocol
from src.library_catalog.data.repositories.protocols import BookRepositoryProtocol


class UnitOfWorkProtocol(Protocol):
    books: BookRepositoryProtocol

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...

    async def __aenter__(self) -> "UnitOfWorkProtocol": ...

    async def __aexit__(self, *args) -> None: ...
