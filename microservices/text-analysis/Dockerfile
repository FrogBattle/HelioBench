FROM smizy/scikit-learn:0.22-alpine

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql \
    && apk add postgresql-dev \
    && apk add bash \
    && pip install psycopg2 \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install Pillow 
RUN pip3 install pandas nltk matplotlib numpy sklearn seaborn mglearn --user

# Install Node explorer
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.2.2/node_exporter-1.2.2.linux-amd64.tar.gz
RUN tar xvfz node_exporter-1.2.2.linux-amd64.tar.gz
COPY . .
RUN chmod +x startup_script.sh

CMD [ "./startup_script.sh" ] 