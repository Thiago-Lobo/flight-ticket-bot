FROM ubuntu:18.04

RUN apt update
RUN apt install -y python3 python3-pip
RUN pip3 install python-telegram-bot
RUN pip3 install pyyaml

RUN apt install -y chromium-browser chromium-driver
RUN pip3 install selenium

RUN apt-get install -y locales

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && \
    locale-gen
ENV LANG en_US.UTF-8  
ENV LANGUAGE en_US:en  
ENV LC_ALL en_US.UTF-8  

RUN mkdir /log

ADD test_chromium.py /
ADD telegram_bot.py /
ADD bot-config.yml /

CMD python3 /telegram_bot.py

