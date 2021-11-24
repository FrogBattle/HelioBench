# Reference: https://github.com/instana/robot-shop/tree/master/load-gen
FROM python:3.9

# Some default values
ENV HOST="http://localhost:8080/" \
    SILENT=0 \
    NUM_CLIENTS=1 \
    ERROR=0 \
    RUN_TIME=0
    

WORKDIR /load

COPY requirements.txt /load/

RUN pip install -r requirements.txt

COPY entrypoint.sh /load/
COPY go-api.py /load/
COPY load_data.py /load/

CMD ["./entrypoint.sh"]

