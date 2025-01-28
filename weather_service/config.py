from pydantic_settings import BaseSettings


class Config(BaseSettings):
    # AWS
    aws_endpoint_url: str
    aws_default_region: str = "eu-west-1"
    s3_bucket_name: str = "weather"
    aws_access_key_id: str
    aws_secret_access_key: str
    # Dynamo DB
    dynamodb_table_name: str = "weather_log"

    # WeatherApi
    weatherapi_url: str
    weatherapi_apy_key: str
