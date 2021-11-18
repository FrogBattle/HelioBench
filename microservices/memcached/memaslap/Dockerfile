FROM ubuntu:16.04

# Install libevent needed for memaslap
RUN apt-get update && apt-get install libevent-dev wget build-essential sudo -y
RUN useradd -m docker && echo "docker:docker" | chpasswd && adduser docker sudo
RUN wget https://launchpad.net/libmemcached/1.0/1.0.18/+download/libmemcached-1.0.18.tar.gz && \
    tar -xf libmemcached-1.0.18.tar.gz
RUN cd libmemcached-1.0.18 && sed -i 's/LDFLAGS =/LDFLAGS = -L\/lib64 -lpthread/g' Makefile.in
RUN cd libmemcached-1.0.18 && ./configure --enable-memaslap
RUN cd libmemcached-1.0.18 && sudo make && sudo make install
 
CMD [ "./libmemcached-1.0.18/clients/memaslap", "-s 127.0.0.1:11211" , "-t 20s"]