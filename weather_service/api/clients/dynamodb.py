from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from aioboto3 import Session
from fastapi import Depends, FastAPI, Request
from types_aiobotocore_dynamodb.service_resource import Table

from weather_service.config import Config


@asynccontextmanager
async def lifespan(app: FastAPI, config: Config) -> AsyncGenerator[None, None]:
    session = Session()
    async with session.resource(
        "dynamodb",
        endpoint_url=config.aws_endpoint_url,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        region_name=config.aws_default_region,
    ) as dynamodb_resource:
        app.state.dynamodb_table = await dynamodb_resource.Table(
            config.dynamodb_table_name
        )

        yield


async def get_table(request: Request) -> Table:
    return request.app.state.dynamodb_table


DynamodbTable = Annotated[Table, Depends(get_table)]
