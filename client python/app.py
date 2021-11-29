from flask import Flask
import os
import socket

HOST = '192.168.0.202'  # The server's hostname or IP address
PORT = 42069        # The port used by the server


app = Flask(__name__)

@app.route("/")
def readSensor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)
        print('Received', repr(data))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True,host='0.0.0.0',port=port)

