import Adafruit_DHT
import time

DATA_PIN = 3
SENSOR = Adafruit_DHT.DHT11

while True:

    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, DATA_PIN)

    if ((temperature != None)) and ((humidity != None)):
        print("Temperatura={0:0.1f}ºC | Humedad={1:0.1f}%HR".format(temperature, humidity))
    else:
        print("Falla de lectura. Reintentando...")

    time.sleep(5)
