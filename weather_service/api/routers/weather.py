import logging
from datetime import datetime
from typing import Annotated

import botocore
from fastapi import APIRouter, HTTPException, Query

from weather_service.api.clients import s3, weatherapi
from weather_service.api.clients.dynamodb import DynamodbTable

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get(
    "",
    summary="Retrieve weather in the certain city",
    status_code=200,
)
async def get_weather(
    city: Annotated[str, Query(description="The city name")],
    weather_client: weatherapi.Client,
    s3_client: s3.Client,
    table: DynamodbTable,
):
    logger.info(f"Get the weather of {city}.")
    timestamp = datetime.now().date().isoformat()
    file_name = f"{city.lower()}_{timestamp}.json"

    # try to get weather data from S3
    city_weather = await s3_client.get_weather_file(file_name)
    if city_weather:
        return {city: city_weather}

    # get weather data from WeatherAPI
    try:
        city_weather = await weather_client.get_city_weather(city)
    except weatherapi.WeatherAPIException as ex:
        logger.error(f"Failed to get weather data for: {city}", exc_info=True)
        raise HTTPException(
            ex.code, f"Failed to get weather data or city `{city}` not found"
        ) from ex

    # upload weather file to S3
    try:
        file_url = await s3_client.save_weather(file_name, city_weather)
    except s3.S3Exception as ex:
        raise HTTPException(ex.code, str(ex)) from ex

    # store DynamoDB log event
    try:
        await table.put_item(
            Item={
                "id": datetime.now().isoformat(),
                "city": city,
                "timestamp": timestamp,
                "s3_url": file_url,
            }
        )
    except botocore.exceptions.ClientError as ex:
        logger.error("Failed to store DynamoDB log event", exc_info=True)
        raise HTTPException(500, "Failed to store DynamoDB log event") from ex

    return {city: city_weather}
