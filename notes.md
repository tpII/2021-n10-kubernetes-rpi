Para las pruebas con el sensor, se decidió ejecutar directamente sobre la placa un script en python para comprobar su funcionamiento.

El sensor utilizado es el DHT11, que es un sensor de temperatura y humedad.
La placa elegida para correr el script es la misma que utilizaremos como worker en el cluster.

https://www.mouser.com/datasheet/2/758/DHT11-Technical-Data-Sheet-Translated-Version-1143054.pdf

Se trata de un sensor que puede medir temperaturas en un rango de 0ºC a 50ºC con una precision de ±2ºC y humedades en un rango de 20%HR a 90%HR con una precision de ±5%HR. La resolución minima en ambos casos es de 1ºC y 1%HR respectivamente.

HR = Humedad Relativa

En su paquete original, el sensor requiere de una resistencia de pull up de al rededor de 5k en el pin de datos para funcionar. Sin embargo, la version que nosotros poseemos es la de un modulo que ya cuenta con dicha resistencia, mas un capacitor de desacople ubicado en el pin de alimentación para prevenir fallas por cambios bruzcos en la alimentación (filtro pasa-bajos).

http://tutorialesdeelectronicabasica.blogspot.com/2021/03/que-es-el-condensador-de.html

Para conectarlo, se utilizaron los pines 4 (5V PWR) y 6 (GND) para alimentación, y 5 (GPIO 3) para la transmision de datos.
A su vez, fue necesario instalar los paquetes python3-pip y python3-dev para utilzar el modulo.

El programa de prueba consiste en un simple script que lee los datos del sensor y los muestra por consola. Se realizan lecturas cada 5 segundos.
Un detalle que fue descubierto es que dicho sensor es propenso a fallas al leer, sin importar del tiempo de espera entre lecturas. Por lo tanto, se utilizó una funcion especial de la libreria de Adafruit, la cual realiza 15 lecturas sucesivas en intervalos de 2 segundos hasta obtener una lectura valida. Esto reduce la probabilidad de obtener una lectura erronea.

https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup

las librerias necesarias para la ejecucion del script son Adafruit_DHT y time. Raspbian, por defecto, no trae instalado el manejador de paquetes de python, pip. Por lo tanto, se recomienda proceder con los siguientes comandos antes de correr el script.

    sudo apt-get install python3-dev python3-pip
    sudo python3 -m pip install --upgrade pip setuptools wheel
    sudo pip3 install Adafruit_DHT

El programa de prueva consiste en el siguiente script:

```python

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

```

El mismo se encuentra dentro del archivo dht11_sensor_test.py, dentro del directorio dht11_sensor. Si se decea probarlo, copiar el script dentro de la Raspberry Pi que posea el sensor conectado y simplemente correr el mismo dentro del directorio donde se encuentre guardado mediante el comando:

    python3 dht11_sensor_test.py

## Corriendo el script en un contenedor

Para utilizar dicho script con docker, primero debemos crear una imagen. Y antes de ello, debemos crear un dockerfile para especificar como crearla.

Tambien hay que tener en cuenta que, como el script debe correrse en una raspberry pi, y la imagen va a tener un SO para una arquitectura ARM como es la de nuestra SBC, lo mas eficiente es crear directamente la imagen desde la raspberry pi.

Primero, creamos dentro del mismo directorio donde se encuentra el script.

    touch dockerfile

utilizamos nano para poder editar el archivo.

    nano dockerfile

Y en el mismo colocamos.

```dockerfile
FROM arm32v7/python:3.7.12-buster

COPY dht11_sensor_test.py ./

RUN apt-get update && apt-get install -y python3-pip rpi-gpio

RUN python3 -m pip install --upgrade pip setuptools wheel

RUN pip3 install Adafruit_DHT

CMD [ "python 3", "DHT11_sensor_test.py" ]


```

Corriendo pruebas, nos dimos cuenta que, para funcionar en contenedores de forma adecuada, debemos hacerle una pequeña modificacion a nuestro script.
El mismo funciona, sin embargo, dentro del contenedor, los mensajes de print no se muestran hasta detener el script. Esto se debe a como maneja python los buffers de salida. Por lo tanto, debemos agregar el parametro "flush=True" al print, para que funcione de forma correcta.

El script quedaría asi:

```python
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
```

Una vez creado nuestro dockerfile y modificado el script, podemos crear la imagen.

    docker build -t rpi_dht11_sensor:v1 .

Creada la imagen, procedemos a probarla dentro de un contenedor.

    docker container run --rm --privileged rpi_dht11_sensor:v1

Notece el parametro `--privileged` para que el contenedor pueda acceder a los dispositivos de la raspberry pi. Esto es necesario para poder utilizar los pines GPIO. De todas fomras, no es recomendable utilizar este parametro en un contenedor de forma general.
