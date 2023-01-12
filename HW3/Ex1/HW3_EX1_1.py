import json
import paho.mqtt.client as mqtt_client
import redis
import psutil
import uuid
import time
import random
from time import sleep

import argparse as ap
from datetime import datetime

# Create a new MQTT client


mac_address = hex(uuid.getnode())

broker = 'mqtt.eclipseprojects.io'
port = 1883
topic = "s304915"
client_id = f'python-mqtt-{random.randint(0, 1000)}'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def publish(client):
     msg_count = 0
     while True:
        timestamp =int(time.time())
        battery_level = int(psutil.sensors_battery().percent)
        power_plugged = int(psutil.sensors_battery().power_plugged)

        obj = {
        "mac_address": mac_address,
        "timestamp":timestamp,
        "battery_level":battery_level,
        "power_plugged": power_plugged
        }
        string = json.dumps(obj)
       
   
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)
        status = result[0]
        if status == 0:
             print(f"Send `{msg}` to topic `{topic}`")
             print(f"Buttery Information: {obj}\n")
        else:
             print(f"Failed to send message to topic {topic}")
        msg_count += 1

def run():
    client = connect_mqtt()
    client.loop_start()
    publish(client)

if __name__ == '__main__':
    run()

