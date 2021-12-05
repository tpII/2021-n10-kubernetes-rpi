import Adafruit_DHT
import time

DATA_PIN = 3
SENSOR = Adafruit_DHT.DHT11

for i in range(0, 10):

    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, DATA_PIN)

    if ((temperature != None)) and ((humidity != None)):
        print("Temperatura={0:0.1f}ºC | Humedad={1:0.1f}%HR".format(temperature, humidity, flush=True))
    else:
        print("Falla de lectura. Reintentando...", flush=True)

    time.sleep(5)
