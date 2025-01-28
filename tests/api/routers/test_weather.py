from unittest.mock import ANY, patch

from httpx import AsyncClient
from pytest import fixture


@fixture
async def s3_get_weather_file():
    with patch(
        "weather_service.api.clients.s3.S3Client.get_weather_file",
        return_value={"weather": "data"},
    ) as _mock:
        yield _mock


async def test_weather_endpoint(client: AsyncClient, s3_get_weather_file):
    city_name = "Lviv"

    response = await client.get(f"/weather?city={city_name}")

    assert response.status_code == 200
    assert response.json() == {city_name: ANY}


async def test_get_weather_missing_params(client: AsyncClient):
    response = await client.get("/weather")

    assert response.status_code == 422
