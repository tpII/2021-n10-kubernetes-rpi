FROM arm32v7/python:3.7.12-buster

RUN apt-get update && apt-get install -y python3-pip=18.1-5 rpi.gpio=0.6.5-1

RUN python3 -m pip install --upgrade pip setuptools wheel

RUN pip3 install Adafruit_DHT==1.4.0

COPY dht11_sensor_test.py ./

CMD [ "python3", "DHT11_sensor_test.py" ]
