# Sample Kafka Producer

To run, put a parquet file into the 'data' folder (preferably named `sample_data.parquet`) then build the Docker container. 

`docker build -t kafka-producer .`

Then, you can invoke the container with:

`docker run --env KAFKA_URL=[YOUR_URL_HERE] --env KAFKA_CONN_STRING=[YOUR_CONN_STRING_HERE] --env MINUTES_TO_RUN=1 kafka-producer`

You can override the following environment variables using the `--env VAR=foo` syntax:

| Variable          | Usage                                                                                                                        | Default    |
|-------------------|------------------------------------------------------------------------------------------------------------------------------|------------|
| KAFKA_URL         | The URL of the Event Hub (e.g. `[namespace].servicebus.windows.net:9093`)                                                    | [NONE]     |
| KAFKA_CONN_STRING | The [connection string](https://docs.microsoft.com/en-us/azure/event-hubs/event-hubs-get-connection-string) of the Event Hub | [NONE]     |
| MINUTES_TO_RUN    | The number of minutes to emit events (1 per second)                                                                          | 5          |
| MEAN_RECORDS      | The mean number of records to send each second                                                                               | 200        |
| STD_RECORDS       | The standard deviation of the number of records to send each second                                                          | 25         |
| TOPIC             | The Kafka topic to send the events to                                                                                        | can-frames |
| DATA_PATH         | The path of the parquet file to sample events from                                                                           | `./data/sample_data.parquet` |