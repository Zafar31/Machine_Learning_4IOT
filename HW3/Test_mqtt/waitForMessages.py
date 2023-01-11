import paho.mqtt.client as mqtt
import MyTopicDetails as mtd

# get current topic
myTopic = mtd.returnTopic()

# Subscriber

def on_connect(client, userdata, flags, rc):
  print("Connected with result code "+str(rc))
  client.subscribe(myTopic)

def on_message(client, userdata, msg):
  print(msg.topic + ":            "   + str(msg.payload))
  print(msg.topic + ":   decoded->  " + msg.payload.decode())

client = mqtt.Client()
client.connect("test.mosquitto.org",1883,60)

client.on_connect = on_connect
client.on_message = on_message

client.loop_forever()