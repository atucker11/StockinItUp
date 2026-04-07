import aiohttp

from ..config import settings


class HTTPClient:
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None
        self._timeout = aiohttp.ClientTimeout(total=settings.request_timeout_seconds)

    async def start(self) -> None:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(timeout=self._timeout)

    @property
    def session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            raise RuntimeError("HTTP session has not been started")
        return self._session

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()
