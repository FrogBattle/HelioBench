FROM smizy/scikit-learn:0.22-alpine

RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install Pillow 
RUN pip3 install pandas nltk matplotlib numpy sklearn seaborn mglearn --user
COPY . .
CMD ["python3","run.py"]  
