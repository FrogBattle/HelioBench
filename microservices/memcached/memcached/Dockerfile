FROM memcached:1.6

USER root
RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo
RUN apt update -y && apt-get install wget -y

# Install Prometheus Node explorer
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.2.2/node_exporter-1.2.2.linux-amd64.tar.gz
RUN tar xvfz node_exporter-1.2.2.linux-amd64.tar.gz

COPY ./startup_script.sh .
RUN chmod +x startup_script.sh

USER docker

CMD [ "./startup_script.sh" ] 