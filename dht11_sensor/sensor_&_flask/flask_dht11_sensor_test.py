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
