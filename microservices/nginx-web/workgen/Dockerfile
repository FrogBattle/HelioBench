FROM ubuntu:latest

RUN apt-get update -y
RUN apt-get install apache2-utils -y

COPY entrypoint.sh .
RUN chmod +x ./entrypoint.sh

CMD [ "./entrypoint.sh" ]