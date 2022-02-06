# Reference: https://github.com/instana/robot-shop/tree/master/load-gen
FROM python:3.9

# Some default values
ENV GO_LOAD_TARGET_HOST="http://localhost:8080/" \
    GO_LOAD_NUM_CLIENTS=1 \
    GO_LOAD_RUN_TIME=0 \
    SILENT=0 \
    ERROR=0


WORKDIR /load

COPY requirements.txt /load/

RUN pip install -r requirements.txt

COPY entrypoint.sh /load/
COPY go-api.py /load/
COPY load_data.py /load/

CMD ["./entrypoint.sh"]

