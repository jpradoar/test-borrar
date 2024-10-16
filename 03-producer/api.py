#!/usr/bin/python3
from flask import Flask, jsonify, request, Response, render_template
from functools import wraps
import json
import pika
import datetime
import os
import uuid
import socket
import logging
from prometheus_client import start_http_server, Info
from threading import Thread

# Variables globales
mqtthost = os.environ.get('mqtthost')
mqttvhost = os.environ.get('mqttvhost')
mqttuser = os.environ.get('mqttuser')
mqttpass = os.environ.get('mqttpass')
mqttport = 5672
now = datetime.datetime.now()
dateformat = now.strftime("%Y-%m-%d")
myname = socket.gethostname()
hostname = f"{myname}@{socket.gethostbyname(myname)}"
destination_exchange = os.environ.get('destination_exchange') # Uso de exchange
destination_RK = os.environ.get('destination_RK')
credentials = pika.PlainCredentials(mqttuser, mqttpass)

# Logging
logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def sendmsg(message):
    logging.info(message)

def generate_trace_id():
    return str(uuid.uuid4())

app = Flask(__name__, static_folder="templates")

def check_auth(username, password):
    return username == "admin" and password == "admin"

def not_authenticate():
    logging.error("-   *[Producer] Login Failed")
    return Response('Login fail: User and/or Password are wrong!\n', 401,  {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return not_authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/', methods=['GET','POST'])
def my_form():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        client = request.form['client']
        namespace = f"{client}-ns"
        environment = request.form['environment']
        archtype = request.form['archtype']
        hardware = request.form['hardware']
        product = request.form['product']
        
        data = build_message(client, namespace, environment, archtype, hardware, product)
        
        send_mqtt_msg(destination_exchange, destination_RK, data)
        sendmsg(f"-   *[Producer] {data}")
        
        msginfo = json.dumps({"client": client, "status": "Provisioning", "product": product})
        send_mqtt_msg("event-status", "event-status", msginfo)

        return f"<b>Data sent to mqtt:</b> <br><br> [msg] : {data} <br><br> <a href='/'><button>Back</button></a> <meta http-equiv='refresh' content='3;url=/' />"

def send_mqtt_msg(exchange, routing_key, data):
    connection = None
    try:
        parameters = pika.ConnectionParameters(
            host=mqtthost,
            port=mqttport,
            virtual_host=mqttvhost,
            credentials=credentials,
            connection_attempts=5,
            retry_delay=5
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
        channel.exchange_declare(exchange=exchange, exchange_type='direct', durable=True)
        channel.basic_publish(exchange=exchange, routing_key=routing_key, body=data)
        sendmsg(f'-   *[Producer] Data sent mqtt message to exchange: {exchange} with routing_key: {routing_key}')
    except Exception as e:
        logging.error(f'Failed to send message: {e}')
    finally:
        if connection:
            connection.close()

def build_message(client, namespace, environment, archtype, hardware, product):
    message = {
        "client": client,
        "namespace": namespace,
        "environment": environment,
        "archtype": archtype,
        "hardware": hardware,
        "product": product,
        "MessageAttributes": {
            "event_type": {
                "Type": "String",
                "Value": f"mycompany.{myname}.event.{client}.published"
            },
            "published_on": dateformat,
            "trace_id": generate_trace_id(),
            "retrace_intent": "0"
        },
        "Metadata": {
            "host": hostname,
            "origin": "Cloud",
            "publisher": myname
        }
    }
    return json.dumps(message)

def monitoring():
    metric_info = Info('producer_version', 'build version of producer')
    metric_info.info({'name': 'producer', 'version': '1.0.0', 'owner': 'jpradoar'})
    start_http_server(9090)

def main():
    sendmsg('-   *[Producer] Started')
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    Thread(target=main).start()
    Thread(target=monitoring).start()
