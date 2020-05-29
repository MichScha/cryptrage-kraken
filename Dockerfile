FROM python:3

RUN pip3 install requests
RUN mkdir -p /data
WORKDIR /data
ADD index.py /data
VOLUME ["/data"]
CMD [ "python3", "./kraken.py" ]
#RUN rm /data/temp/*.*
#CMD pwd