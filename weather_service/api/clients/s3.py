import json
import logging
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Annotated

import types_aiobotocore_s3
from aioboto3.session import Session
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import Depends, FastAPI, Request

from weather_service.config import Config

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI, config: Config):
    session = Session()
    logger.info("Init S3 client")
    async with session.client(
        "s3",
        endpoint_url=config.aws_endpoint_url,
        aws_access_key_id=config.aws_access_key_id,
        aws_secret_access_key=config.aws_secret_access_key,
        region_name=config.aws_default_region,
    ) as boto_s3_client:
        app.state.s3_client = S3Client(boto_s3_client, config.s3_bucket_name)

        yield


class S3Exception(Exception):
    def __init__(self, message: str, code: int):
        super().__init__(message)
        self.code = code


class S3Client:
    """Asynchronous AWS S3 client."""

    _client: types_aiobotocore_s3.S3Client

    def __init__(self, boto_s3_client: types_aiobotocore_s3.S3Client, bucket: str):
        self._client = boto_s3_client
        self._bucket = bucket

    async def save_weather(self, file_name: str, data: dict) -> str:
        """Save a JSON file either to S3.

        :param file_name: name of the file to save.
        :param data: data to save.
        :return: path to the saved file.
        """
        logger.info("Upload file to S3", extra={"file_name": file_name})
        json_data = json.dumps(data)
        # set TTl for 5 min
        expires = datetime.now() + timedelta(minutes=5)
        try:
            await self._client.put_object(
                Bucket=self._bucket,
                Key=file_name,
                Body=json_data,
                ContentType="application/json",
                Expires=expires,
            )
            return f"s3://{self._bucket}/{file_name}"
        except (BotoCoreError, ClientError):
            logger.error("Failed to upload file to S3", exc_info=True)
            raise S3Exception("Failed to upload file to S3", 500) from None

    async def get_weather_file(self, file_name: str) -> dict | None:
        """Retrieve the specified weather S3 file.

        :param file_name: name of the file object.
        :return: file object content
        """
        logger.info("Get file from S3", extra={"file_name": file_name})
        try:
            obj = await self._client.get_object(
                Bucket=self._bucket,
                Key=file_name,
                ResponseContentType="application/json",
            )
            data = await obj["Body"].read()
            return json.loads(data)
        except self._client.exceptions.NoSuchKey:
            logger.info(f"Weather file`{file_name}` not found", exc_info=True)
            return None


async def get_client(request: Request) -> S3Client:
    return request.app.state.s3_client


Client = Annotated[S3Client, Depends(get_client)]
