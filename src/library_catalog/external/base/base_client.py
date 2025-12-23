from abc import ABC, abstractmethod
import httpx
import logging
import asyncio


class BaseApiClient(ABC):
    """
    Базовый класс для HTTP клиентов внешних API.

    Включает:
    - Retry логику
    - Обработку ошибок
    - Логирование
    - Timeout management
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        retries: int = 3,
        backoff: float = 0.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._client = httpx.AsyncClient(timeout=self.timeout)
        self.logger = logging.getLogger(self.client_name())

    @abstractmethod
    def client_name(self) -> str:
        """Имя клиента для логирования."""
        pass

    def _build_url(self, path: str) -> str:
        """Построить полный URL."""
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    async def request(
        self,
        method: str,
        path: str,
        params: dict | None = None,
        json: dict | None = None,
        headers: dict | None = None,
    ) -> dict:
        """
        Выполнить HTTP запрос с retry логикой.

        Raises:
            httpx.TimeoutException: При таймауте
            httpx.HTTPError: При HTTP ошибке
        """
        url = self._build_url(path)

        for attempt in range(self.retries):
            try:
                self.logger.debug(
                    f"[Attempt {attempt + 1}/{self.retries}] {method} {url}"
                )

                response = await self._client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )

                response.raise_for_status()

                # Обработка пустых ответов
                if response.status_code == 204 or not response.content:
                    return {}

                return response.json()

            except httpx.HTTPStatusError as e:
                # 5xx ошибки - retry
                if e.response.status_code >= 500 and attempt < self.retries - 1:
                    wait_time = self.backoff * (2**attempt)
                    self.logger.warning(f"Server error, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"HTTP {e.response.status_code}: {e}")
                    raise

            except httpx.TimeoutException:
                if attempt == self.retries - 1:
                    self.logger.error(f"Timeout after {self.retries} attempts")
                    raise

                wait_time = self.backoff * (2**attempt)
                self.logger.info(f"Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.RequestError as e:
                self.logger.error(f"Request error: {e}")
                if attempt == self.retries - 1:
                    raise

                wait_time = self.backoff * (2**attempt)
                await asyncio.sleep(wait_time)

    async def _get(self, path: str, **kwargs) -> dict:
        """GET запрос."""
        return await self.request("GET", path, **kwargs)

    async def close(self) -> None:
        """Закрыть HTTP клиент."""
        await self._client.aclose()
