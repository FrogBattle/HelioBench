FROM tensorflow/tensorflow:latest
RUN apt-get install wget

# Install Node explorer
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.2.2/node_exporter-1.2.2.linux-amd64.tar.gz
RUN tar xvfz node_exporter-1.2.2.linux-amd64.tar.gz

COPY ./requirements.txt ./
RUN pip3 install -r requirements.txt

COPY . .
RUN chmod +x startup_script.sh
CMD [ "./startup_script.sh" ] 