FROM python:3
WORKDIR /usr/local/app
ADD . /usr/local/app
RUN apt update && apt install python3-pip -y
RUN pip3 install -r requirements.txt

CMD ["./entrypoint.sh"]

EXPOSE 9080:9080
