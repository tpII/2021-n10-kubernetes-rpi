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

las librerias necesarias para la ejecucion del script son Adafruit_DHT y time. Raspbian, por defecto, no trae instalado el manejador de paquetes de python, pip. Por lo tanto, se recomienda proceder con los siguientes comandos antes de correr el script.

    sudo apt-get install python3-dev python3-pip
    sudo python3 -m pip install --upgrade pip setuptools wheel
    sudo pip3 install Adafruit_DHT

El programa de prueva consiste en el siguiente script:

