import datetime
import json
import logging
import os
import random
import sys
import time
from pathlib import Path

import pandas as pd
import typer
from confluent_kafka import Producer

KAFKA_URL = os.environ.get(
    "KAFKA_URL")
CONN_STRING = os.environ.get(
    "KAFKA_CONN_STRING")

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(sys.stdout)
logger.addHandler(stream_handler)

KAFKA_CONF = {
    'bootstrap.servers': KAFKA_URL,
    'security.protocol': 'SASL_SSL',
    'ssl.ca.location': '/usr/lib/ssl/certs/ca-certificates.crt',
    'sasl.mechanism': 'PLAIN',
    'sasl.username': '$ConnectionString',
    'sasl.password': CONN_STRING,
    'client.id': 'can-frame-dummy-generator'
}


def delivery_callback(err, msg):
    if err:
        logger.error('%% Message failed delivery: %s\n' % err)
    else:
        logger.info(
            '%% Message delivered to %s [%d] @ %o\n' % (msg.topic(), msg.partition(), msg.offset()))


def get_samples(df, num_records_mean: int, num_records_std: int) -> list:
    num_records = int(random.gauss(num_records_mean, num_records_std))

    samp = df.sample(num_records)
    samp['epoch_usec'] = samp.id.apply(lambda x: int(time.time()*1_000_000))

    return samp.to_dict(orient='records')


def main(
    minutes_to_run: int = 5,
    topic: str = 'can-frames',
    data_file: Path = typer.Option(Path('./data/sample_data.parquet'), file_okay=True, dir_okay=False, exists=True),
    num_records_mean: int = 200,
    num_records_std: int = 25,
    verbose: bool = False
):
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    logger.debug(f"--minutes-to-run = {minutes_to_run}")
    logger.debug(f"--topic = {topic}")
    logger.debug(f"--data-file = {data_file}")
    logger.debug(f"--num-records-mean = {num_records_mean}")
    logger.debug(f"--num-records-std = {num_records_std}")

    if KAFKA_URL is None or CONN_STRING is None:
        raise AttributeError('Missing one or more required environment variables: "KAFKA_URL" or "KAFKA_CONN_STRING"'
                             ' set these via docker run with the "-env" parameter')

    end_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes_to_run)

    df = pd.read_parquet(data_file)

    # Create Producer instance
    p = Producer(**KAFKA_CONF)

    while datetime.datetime.now() < end_time:
        samples = get_samples(
            df=df,
            num_records_mean=num_records_mean,
            num_records_std=num_records_std
        )

        message = {'handler': 'canbus',
                   'data': samples
                   }

        try:
            p.produce(topic, json.dumps(message), callback=delivery_callback)
        except BufferError:
            logger.error(
                '%% Local producer queue is full (%d messages awaiting delivery): try again\n' % len(p))
        p.poll(0)

        time.sleep(1)

    p.flush()


if __name__ == '__main__':
    typer.run(main)
