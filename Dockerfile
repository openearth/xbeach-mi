FROM ubuntu:16.04

RUN apt-get update && apt-get install -y git python3 python3-pip 

COPY ./ /opt/xbeach-mi

RUN	pip3 install git+https://github.com/openearth/bmi-python.git && \
	pip3 install git+https://github.com/openearth/mmi-python.git && \
	cd /opt/xbeach-mi && python3 setup.py install

EXPOSE 50010-50020

WORKDIR /data

CMD mmi-runner --port 50010 --bmi-class xbeachmi.model.XBeachMI config.json
