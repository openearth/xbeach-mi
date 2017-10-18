FROM ubuntu:16.04

RUN apt-get update && apt-get install -y git python3 python3-pip 

COPY ./ /opt/xbeach-mi

RUN	pip3 install mmi \
	&& cd /opt/xbeach-mi && python3 setup.py install

WORKDIR /data

CMD ["xbeach-mi", "config.json", "--verbose=1"]