FROM arm32v7/python:3.7.12-buster

RUN apt-get update && apt-get install -y python3-pip rpi-gpio

RUN python3 -m pip install --upgrade pip setuptools wheel

RUN pip3 install Adafruit_DHT

COPY dht11_sensor_test.py ./

CMD [ "python 3", "DHT11_sensor_test.py" ]
