Para las pruebas con el sensor, se decidió ejecutar directamente sobre la placa un script en python para comprobar su funcionamiento.

El sensor utilizado es el DHT11, que es un sensor de temperatura y humedad.
La placa elegida para correr el script es la misma que utilizaremos como worker en el cluster.

<https://www.mouser.com/datasheet/2/758/DHT11-Technical-Data-Sheet-Translated-Version-1143054.pdf>

Se trata de un sensor que puede medir temperaturas en un rango de 0ºC a 50ºC con una precision de ±2ºC y humedades en un rango de 20%HR a 90%HR con una precision de ±5%HR. La resolución minima en ambos casos es de 1ºC y 1%HR respectivamente.

HR = Humedad Relativa

En su paquete original, el sensor requiere de una resistencia de pull up de al rededor de 5k en el pin de datos para funcionar. Sin embargo, la version que nosotros poseemos es la de un modulo que ya cuenta con dicha resistencia, mas un capacitor de desacople ubicado en el pin de alimentación para prevenir fallas por cambios bruzcos en la alimentación (filtro pasa-bajos).

<http://tutorialesdeelectronicabasica.blogspot.com/2021/03/que-es-el-condensador-de.html>

Para conectarlo, se utilizaron los pines 4 (5V PWR) y 6 (GND) para alimentación, y 5 (GPIO 3) para la transmision de datos.
A su vez, fue necesario instalar los paquetes python3-pip y python3-dev para utilzar el modulo.

El programa de prueba consiste en un simple script que lee los datos del sensor y los muestra por consola. Se realizan lecturas cada 5 segundos.
Un detalle que fue descubierto es que dicho sensor es propenso a fallas al leer, sin importar del tiempo de espera entre lecturas. Por lo tanto, se utilizó una funcion especial de la libreria de Adafruit, la cual realiza 15 lecturas sucesivas en intervalos de 2 segundos hasta obtener una lectura valida. Esto reduce la probabilidad de obtener una lectura erronea.

<https://learn.adafruit.com/dht-humidity-sensing-on-raspberry-pi-with-gdocs-logging/python-setup>

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

Dockerfile Reference: https://docs.docker.com/engine/reference/builder/

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

Notece el parametro `--privileged` para que el contenedor pueda acceder a los dispositivos de la raspberry pi. Esto es necesario para poder utilizar los pines GPIO.  
Existen dos formas basicamente de lograr esto. Una es eligiendo el dispositivo, reemplazando la sentencia `--privileged` por `--devices /dev/gpiomem`. Esta ultima forma es la mas recomendada para estos casos, ya que simplemente comparte con el contenedor el dispositivo fisico del host. Sin embargo, las limitaciones de la imagen base impidieron que la imagen final pueda acceder al archivo correspondiente a dicho dispositivo. `/dev/gpiomem`, incluso habiendo modificado los grupos del sistema y de la imagen como es debido. Concluimos que el problema puede deberse a que no utilizamos una imagen base con la arquitectura provista por raspbian, sino una basada en debian.
El metodo de `--privileged` dió buenos resultados, funcionando de forma automatica. De todas fomras, no es recomendable utilizar este parametro en un contenedor de forma general. Esto suele ser una tecnica insegura y una practica desaconsejada, ya que el contenedor correrá mas cerca del sistema operativo del host, perdiendo ciertas ventajas de seguridad propias de los contenedores.
En nuestro caso, dado que nos encontramos en un ambiente controlado y cerrado, podemos darnos el lujo de utilizar el parametro `--privileged`.

Docker Privileged: <https://phoenixnap.com/kb/docker-privileged>

## Pagia web del sensor con Flask

Teniendo nuestro sensor funcionando, procedemos a crear una pagina web que muestre los datos del sensor. Para ello, utilizaremos la librería Flask.

Fask quick start: https://flask.palletsprojects.com/en/2.0.x/quickstart/
Flask Tutorial: https://pythonbasics.org/flask-tutorial-hello-world/

    pip3 install Flask

Luego, aplicamos algunas modificaciónes a nuestro script para que sea ejecutable como una aplicación web.

    nano dht11_sensor_test.py

```python
# import the Flask class from the flask module
from flask import Flask, render_template
import Adafruit_DHT

DATA_PIN = 3
SENSOR = Adafruit_DHT.DHT11

# create the application object
app = Flask(__name__)

# use decorators to link the function to a url
@app.route('/')
def home():
    humidity, temperature = Adafruit_DHT.read_retry(SENSOR, DATA_PIN)

    if ((temperature != None)) and ((humidity != None)):
        return("Temperatura={0:0.1f}ºC | Humedad={1:0.1f}%HR".format(temperature, humidity))
    else:
        return("Falla de lectura. Reintentando...")

# start the server with the 'run()' method
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
```

Luego simplemente corremos el script.

    python3 dht11_sensor_test.py

Nos dirigimos a un navegador web y colocamos la dirección de nuestra pagina web.

    {ip_nodo_host}:5000

A continuación, metemos nuestro nuevo script en una imagen de docker. Para ello, editamos un dockerfile.

    nano dockerfile

```dockerfile
FROM arm32v7/python:3.7.12-buster

RUN apt-get update && apt-get install -y python3-pip rpi.gpio

RUN python3 -m pip install --upgrade pip setuptools wheel

RUN pip3 install Adafruit_DHT Flask

COPY flask_dht11_sensor_test.py ./

CMD [ "python3", "flask_dht11_sensor_test.py" ]
```

Luego, creamos la imagen.

    docker build -t flask_dht11:v1 .

Una vez terminada, corremos un contenedor en docker para probarla. En este caso, cambiaremos

    docker container run --rm --privileged -p 4000:5000 flask_dht11:v1

## Subiendo la imagen a docker hub

Docker hub: https://hub.docker.com/
Docker hub quickstart: https://docs.docker.com/docker-hub/
Docker Repositories: https://docs.docker.com/docker-hub/repos/

El tener la imagen creada por nosotros subida a un repositorio en docker hub, permite facilitar el proceso de deployment en otras plataformas, incluyendo el cluster en si.

Para ello, uno debe tener una cuenta en docker hub. Una vez creada, seleccionamos "Create Reopistory" y le damos un nombre. en nuestro caso, llamaremos a nuestro repositorio "flask-dht11-rpi".

A continuanción, cambiamos el tag de la imagen creada por uno que posea todas las caracteristicas estandar para el repositorio.

    docker image tag imagen_fuente:tag_fuente nombre_de_usuario/nombre_repositorio:tag_destino

El tag puede ser el mismo que el tag de la imagen original, o puede ser uno nuevo.
Por ejemplo, en nuestro caso, el comando quedaría

    docker image tag flask_dht11:v1 alcaolpg/flask-dht11-rpi:latest

Luego, iniciamos sesion y subimos el archivo a docker hub.

    docker login

    docker push nombre_de_usuario/nombre_repositorio:tag_destino

Al finalizar la carga, cerramos sesion.

    docker logout

Imagen subida a docker hub: https://hub.docker.com/repository/docker/alcaolpg/flask-dht11-rpi

## Deployment en el cluster de kubernetes

Al momento de lanzar la aplicación en el cluster, es importante notar que existe un tipo de archivo de vital importancia para el proceso. Los archivos .yaml (Yet Another Markup Language o YAML Ain't Markup Language) son una forma de definir los servicios y los contenedores que se encuentran en el cluster de forma rapida y entendible.

What is YAML?: https://www.redhat.com/en/topics/automation/what-is-yaml
Understanding Kubernetes Objects: https://kubernetes.io/docs/concepts/overview/working-with-objects/kubernetes-objects/

En nuestro caso, debemos crear un archivo de configuración de contenedores y otro de servicios. El de contenedores se encargará de crear las pods que contienen nuestra aplicación, con todas sus caracteristicas necesarias. El de servicios se encargará de definir un servicio que permita acceder a la aplicación desde el exterior.
Al igual que con docker, es necesario que la capsula que contenga la aplicación funcione en modo privilegiado.

Pod Security Polices: https://kubernetes.io/docs/concepts/policy/pod-security-policy/#privileged
Kubernetes Privileged Pod Practical Example: https://www.golinuxcloud.com/kubernetes-privileged-pod-examples/

    nano sensor.yaml

Dentro del mismo, escrivimos:

```yaml
apiVersion: apps/v1 # Version de Kubernetes para este objeto
kind: Deployment # Tipo de objeto
metadata:
  name: sensor # Nombre del objeto
  namespace: default # Nombre del espacio de trabajo
spec:
  replicas: 1 # Cantidad de pods que se crearan
  selector:
    matchLabels:
      app: sensor # Nombre del contenedor para identificacion de la aplicacion
  template:
    metadata:
      labels:
        app: sensor # Nombre del contenedor
    spec:
      containers:
        - name: flask-dht11-rpi # Nombre de la aplicacion
          image: alcaolpg/flask-dht11-rpi:latest # Nombre de la imagen que debe buscarse en docker hub
          ports:
            - containerPort: 5000 # Puerto utilizado para comunicarse con la aplicacion
              protocol: TCP
          securityContext:
            privileged: true # Permite que el contenedor acceda a los dispositivos GPIO
      nodeSelector:
        dhtsensor: "yes" # Selecciona los nodos que poseen el dispositivo DHT11
```

Paremonos en la ultima sentencia de la seccion "nodeSelector". En nuestro caso, el sensor se encuentra conectado a una unica placa Raspberry Pi 3B+ mediante GPIO. Por lo tanto, si querémos que el sistema sea capaz de obtener información del sensor, debemos especificar que el nodo debe tener el dispositivo DHT11. Para ello, nos valemos de la posibilidad de usar etiquetas o labels para cada nodo.

Assigning pods to nodes: https://kubernetes.io/docs/concepts/scheduling-eviction/assign-pod-node/
How to use Node Selectors in Kubernetes: https://www.howtoforge.com/use-node-selectors-in-kubernetes/

Desde el nodo maestro, agregaremos una etiqueta para que el nodo seleccionado por el sistema sea el correcto.

    kubectl label node [nombre del nodo con el sensor] nombre_del_campo_lavel=lavel_a_usar

En nuestro caso, la sentencia anterior quedaría:

    kubectl label node worker1 dhtsensor=yes

Para comprovar la etiqueta, podemos usar el comando:

    kubectl get nodes --show-labels

Creada nuestra etiqueta, procedemos a lanzar la aplicacion en el cluster.

    kubectl apply -f sensor.yaml

Podemos ver los resultados en la consola de kubernetes.

    kubectl get pods -o wide

Para poder acceder a la aplicación, todavia debemos crear el servicio que se encargue de redireccionar las solicitudes del exterior al contenedor de la apliacion. Este tipo de servicio se llama "nodeport".

    nano sensor_nodeport.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: sensor-nodeport # Nombre del servicio
  namespace: default
spec:
  type: NodePort
  selector:
    app: sensor # Nombre del contenedor que identfica a la aplicacion
  ports:
    - port: 5000 # Puerto utilizado para comunicarse con la aplicacion
      targetPort: 5000 # Puerto del contenedor de la aplicacion
      nodePort: 30001 # Puerto utilizado para acceder al contenedor desde el exterior
```

Una vez que creamos el servicio, podemos lanzarlo en el cluster.

    kubectl apply -f sensor_nodeport.yaml

Podemos comprovar que el servicio esté corriendo utilizando:

        kubectl get services

Por ultimo, accedemos desde el exterior al contenedor de la aplicacion. Desde una computadora dentro de la misma red, accedemos utilizando la direccion ip de cualquier nodo del cluster desde un navegador web.

    http://[ip del nodo]:30001

En caso de querer eliminar el servicio o el contenedor, podemos hacerlo con los comandos:

    kubectl delete pod [nombre del contenedor]

    kubectl delete deployment [nombre del contenedor]

    kubectl delete service [nombre del servicio]

Removing data collector Docker container / Kubernetes pod: https://www.ibm.com/docs/en/cloud-paks/cp-management/2.3.x?topic=monitoring-removing-data-collector-docker-container-kubernetes-pod
