FROM arm32v7/python:3.7.12-buster

COPY flask_dht11_sensor_test.py ./

RUN apt-get update && apt-get install -y python3-pip rpi-gpio

RUN python3 -m pip install --upgrade pip setuptools wheel

RUN pip3 install Adafruit_DHT Flask

CMD [ "python 3", "flask_dht11_sensor_test.py" ]
