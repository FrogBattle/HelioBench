FROM nginx:stable

RUN apt update -y && apt-get install wget -y
RUN rm /etc/nginx/conf.d/default.conf
COPY pages /usr/share/nginx/html
COPY nginx.conf /etc/nginx
RUN adduser --system --no-create-home --shell /bin/false --group --disabled-login www
RUN mkdir /etc/nginx/logs && cd /etc/nginx/logs && touch error.log 

# Install Node explorer
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.2.2/node_exporter-1.2.2.linux-amd64.tar.gz
RUN tar xvfz node_exporter-1.2.2.linux-amd64.tar.gz
COPY ./startup_script.sh .
RUN chmod +x startup_script.sh

CMD [ "./startup_script.sh" ] 