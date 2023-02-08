"""
my_dict = {
        "mac_address":mac_address,
        "timestamp":timestamp,
        "battery_level":battery_level,
        "power_plugged": power_plugged
        }
"""

import paho.mqtt.client as mqtt
import redis
import json

REDIS_HOST = 'redis-18326.c55.eu-central-1-1.ec2.cloud.redislabs.com'
REDIS_PORT = 18326
REDIS_USERNAME = 'default'
REDIS_PASSWORD = '4BjSUT7diE4N72W5WPpJcP7hAH41IPc4'

broker = 'mqtt.eclipseprojects.io'
port = 1883
topic = "s304915"

mac_addresses = set()

redis_client = redis.Redis(
    host=REDIS_HOST, 
    port=REDIS_PORT, 
    username=REDIS_USERNAME, 
    password=REDIS_PASSWORD)
is_connected = redis_client.ping()
print('Redis Connected:', is_connected)

# Subscriber

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe(topic)

def on_message(client, userdata, msg):
    # print("5")
    # print(msg.topic + ":            "   + str(msg.payload))
    # print(type(str(msg.payload)))
    # print(msg.topic + ":   decoded->  " + msg.payload.decode())

    myJSON = json.loads(str(msg.payload.decode()))
    global mac_addresses
    

    """
    json get my infos
    """
    mac_address     =       myJSON["mac_address"]
    timestamp       =   int(myJSON["timestamp"])
    battery_level   =       myJSON["battery_level"]
    power_plugged   =       myJSON["power_plugged"]

    # print(myJSON["mac_address"])
    # print(myJSON["timestamp"])
    # print(myJSON["battery_level"])
    # print(myJSON["power_plugged"])
    timeseries_name_battery = mac_address+':battery'
    timeseries_name_power   = mac_address+':power'
    # print(timeseries_name)
    """
    send to redis
    """
    if mac_address not in mac_addresses:
        print("******************* Before:",mac_addresses)
        mac_addresses.add(mac_address)
        print("***************     After:",mac_addresses)
        try:
            redis_client.ts().create(timeseries_name_battery, chunk_size=128, duplicate_policy='LAST')
            redis_client.ts().create(timeseries_name_power, chunk_size=128, duplicate_policy='LAST')
        except redis.ResponseError:
            # print("Probably you already have these timeseries")
            pass
    try:
        # redis_client.ts().create(timeseries_name, chunk_size=128, duplicate_policy='LAST')
        # redis_client.ts().create(timeseries_name, chunk_size=128, duplicate_policy='LAST')
        redis_client.ts().add(timeseries_name_battery, timestamp, battery_level)
        redis_client.ts().add(timeseries_name_power, timestamp, power_plugged)
    except redis.exceptions.ResponseError as e:
        # print(e)
        pass

# print("1")
client = mqtt.Client()
# print("2")
client.connect(broker,port,60)

# print("3")
client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()