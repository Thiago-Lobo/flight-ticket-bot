FROM ubuntu:18.04

RUN apt update
RUN apt install -y python3 python3-pip
RUN pip3 install python-telegram-bot
RUN pip3 install pyyaml

RUN apt install -y chromium-browser chromium-driver
RUN pip3 install selenium

CMD /bin/bash
