FROM smizy/scikit-learn:0.22-alpine

# RUN apk add build-base python3-dev zlib
# # RUN apk add python-dev python3-dev \
# #      build-essential libssl-dev libffi-dev \
# #      libxml2-dev libxslt1-dev zlib1g-dev \
# #      python-pip
RUN apk update \
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql \
    && apk add postgresql-dev \
    && pip install psycopg2 \
    && apk add jpeg-dev zlib-dev libjpeg \
    && pip install Pillow 
    # && apk del build-deps
RUN pip3 install pandas nltk matplotlib numpy sklearn seaborn mglearn --user
COPY . .
CMD ["python3","run.py"]  
