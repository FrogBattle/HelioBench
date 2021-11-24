FROM golang:1.12

ENV WORKDIR=/go/src/app

WORKDIR ${WORKDIR}

COPY . .
ENV GOBIN=${WORKDIR}/bin

RUN go get -v -u github.com/gorilla/mux
RUN go install main.go


RUN apt update -y && apt-get install wget -y

# Install Prometheus Node explorer
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.2.2/node_exporter-1.2.2.linux-amd64.tar.gz
RUN tar xvfz node_exporter-1.2.2.linux-amd64.tar.gz

COPY ./startup_script.sh .
RUN chmod +x startup_script.sh

CMD [ "./startup_script.sh" ]
