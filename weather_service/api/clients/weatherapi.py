import logging
from contextlib import asynccontextmanager
from typing import Annotated, Any

import httpx
from fastapi import Depends, FastAPI, Request

from weather_service.config import Config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI, config: Config):
    logger.info("Init WeatherAPI client")
    async with httpx.AsyncClient(base_url=config.weatherapi_url) as httpx_client:
        app.state.weather_client = WeatherAPIClient(
            httpx_client, config.weatherapi_apy_key
        )

        yield


class WeatherAPIException(Exception):
    def __init__(self, code: int):
        self.code = code


class WeatherAPIClient:
    """Asynchronous client for interacting with the WeatherAPI."""

    def __init__(self, client: httpx.AsyncClient, api_key: str):
        self.client = client
        self.api_key = api_key
        self._current_weather_url = "current.json"

    async def _get(
        self, endpoint: str, params: dict[str, str] | None = None
    ) -> dict[str, Any]:
        """Internal method to make GET requests.

        :param endpoint: API endpoint
        :param params: query parameters to include in the request.
        :return: response JSON data.
        """
        if params is None:
            params = {}
        params["key"] = self.api_key
        try:
            response = await self.client.get(endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as ex:
            logger.error("Failed to get weather data", exc_info=True)
            raise WeatherAPIException(code=ex.response.status_code) from ex  # type: ignore

    async def get_city_weather(self, city: str) -> dict:
        """Get current weather for a specified city.

        :param city: the city name location query.
        :return: weather data as dictionary.
        """
        logger.info("Get current weather data", extra={"city": city})
        return await self._get(self._current_weather_url, params={"q": city})


async def get_client(request: Request) -> WeatherAPIClient:
    return request.app.state.weather_client


Client = Annotated[WeatherAPIClient, Depends(get_client)]
