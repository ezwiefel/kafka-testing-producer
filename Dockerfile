FROM python:3.8.13

ENV MINUTES_TO_RUN=5
ENV MEAN_RECORDS=200
ENV STD_RECORDS=25
ENV TOPIC=can-frames
ENV DATA_PATH=./data/sample_data.parquet

RUN apt-get update && \
    apt-get install -y openssl libssl-dev build-essential librdkafka-dev

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir /usr/src/app
WORKDIR /usr/src/app
COPY . .

CMD python send_messages.py --minutes-to-run ${MINUTES_TO_RUN} --num-records-mean ${MEAN_RECORDS} --num-records-std ${STD_RECORDS} --topic ${TOPIC} --data-file ${DATA_PATH}