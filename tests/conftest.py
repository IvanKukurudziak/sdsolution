from collections.abc import AsyncGenerator
from unittest.mock import patch

from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from pytest import fixture


@fixture
def environ_dict():
    """Environment variables specific to the Engage app"""
    return dict(
        AWS_ENDPOINT_URL="http://localhost",
        AWS_DEFAULT_REGION="eu-west-1",
        AWS_ACCESS_KEY_ID="test-key",
        AWS_SECRET_ACCESS_KEY="test-secret-key",
        S3_BUCKET_NAME="test",
        DYNAMODB_TABLE_NAME="test",
        WEATHERAPI_URL="test.weatherapi/",
        WEATHERAPI_APY_KEY="test",
    )


@fixture(autouse=True)
def environ(environ_dict):
    with patch.dict("os.environ", environ_dict, clear=True):
        yield environ_dict


@fixture(scope="session")
async def app():
    from weather_service.main import app

    async with LifespanManager(app):
        yield app


@fixture(scope="session")
async def client(app) -> AsyncGenerator[AsyncClient, None]:
    """HTTPX async client to test the app."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test.local"
    ) as async_client:
        yield async_client


@fixture(scope="session")
def config():
    from weather_service.config import Config

    config = Config()
    return config
