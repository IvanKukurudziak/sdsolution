# Weather API Service
This project is a simple weather API service built with FastAPI. 
It fetches weather data from an external public API, caches the responses in S3, and logs the events in DynamoDB. 

## Features
Fetch weather data asynchronously from a public API.
Cache weather data in S3
Log events (city name, timestamp, file path) in DynamoDB
Automatically cache weather data for 5 minutes to reduce API calls.
Fully asynchronous and designed for high traffic.


### Prerequisites

Set up your environment variables in a .env file and export:
`. ./.env`

Obtain a Weather API key from WeatherAPI.

### How to Run the App Locally
1. Clone the Repository
```bash
git clone <repository_url>
cd <repository_folder>
```
2. To ensure that your LocalStack init script is executable run:
```bash
 chmod +x ./localstack-script.sh
 ```

3. Build and Run the Docker Containers

```bash
docker-compose up --build
```

4. Access the API
The FastAPI app will be running at: http://localhost:8000.

Use the /weather endpoint to fetch weather data:
```bash

curl -X GET "http://localhost:8000/weather?city=Lviv"
```

Access the interactive API documentation:
Swagger UI http://localhost:8000/docs
