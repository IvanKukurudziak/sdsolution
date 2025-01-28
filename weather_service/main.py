import logging
from contextlib import AsyncExitStack, asynccontextmanager

from fastapi import FastAPI

from weather_service.api.clients import dynamodb, s3, weatherapi
from weather_service.api.routers import weather
from weather_service.config import Config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("App startup")
    config = Config()
    async with AsyncExitStack() as stack:
        # init weatherAPI client
        await stack.enter_async_context(weatherapi.lifespan(app, config))
        # init S3 client
        await stack.enter_async_context(s3.lifespan(app, config))
        # init Dynamo DB client
        await stack.enter_async_context(dynamodb.lifespan(app, config))

        yield
        logger.info("App shutting down")


app = FastAPI(
    title="Weather API Service", openapi_url="/docs/openapi.json", lifespan=lifespan
)

# routers
app.include_router(weather.router)
