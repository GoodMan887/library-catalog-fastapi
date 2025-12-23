from typing import Optional
import logging

from ..external.openlibrary.client import OpenLibraryClient
from ..core.config import settings

logger = logging.getLogger(__name__)


class ClientsManager:
    """
    Менеджер для управления lifecycle внешних клиентов.

    Преимущества:
    - Lazy initialization
    - Proper cleanup при shutdown
    - Легко добавить новые клиенты (GoogleBooks, etc.)
    - Можно мокировать в тестах
    """

    def __init__(self):
        self._openlibrary: Optional[OpenLibraryClient] = None

    def get_openlibrary(self) -> OpenLibraryClient:
        """
        Получить OpenLibrary клиент (lazy initialization).

        Создается только при первом обращении и переиспользуется.
        """
        if self._openlibrary is None:
            logger.info("Initializing OpenLibrary client")
            self._openlibrary = OpenLibraryClient(
                base_url=settings.openlibrary_base_url,
                timeout=settings.openlibrary_timeout,
            )
        return self._openlibrary

    async def close_all(self):
        """
        Закрыть все клиенты.

        Вызывается при shutdown приложения.
        """
        if self._openlibrary:
            logger.info("Closing OpenLibrary client")
            await self._openlibrary.close()
            self._openlibrary = None


# Глобальный экземпляр менеджера
clients_manager = ClientsManager()
