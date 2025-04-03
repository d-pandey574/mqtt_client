import paho.mqtt.client as mqtt
import json
import time
import datetime
import pytz

# MQTT broker information
broker_address = "mqtt.eclipseprojects.io"
port = 1883
client_id = "DEMO locator"

# Create an MQTT client instance
client = mqtt.Client(client_id)

# Set timezone
gmt = pytz.timezone('GMT')
# Get the current time
current_time_gmt = datetime.datetime.now(gmt)


working_json = {
    "timstamp": current_time_gmt.strftime('%Y-%m-%d %H:%M:%S %Z'),
    "latitude": 41.37779323665853, 
    "longitude": 2.1464843181438202
}
#working_json = json.loads(locator_status_data)

# Callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    # Subscribe to a topic when connected
    # Publish a message to a topic
    #client.publish("your_topic", "your_message")
    #client.subscribe("your_topic")

# Callback function for when a message is received from the broker
def on_message(client, userdata, msg):
    print("Received message on topic "+msg.topic+": "+str(msg.payload))
    # For now we accept no commands form others so we just print the message and forget it

# Set callback functions
client.on_connect = on_connect
client.on_message = on_message

# Connect to the broker
client.connect(broker_address, port, 60)

# Start the MQTT loop to process messages
client.loop_start()

status_topic = "sp_v1/spain/bracelona/abcdef012345"

# To keep the script running
while True:
    # Update the timestamp before sending status message
    current_time_gmt = datetime.datetime.now(gmt)
    working_json["timstamp"] = current_time_gmt.strftime('%Y-%m-%d %H:%M:%S %Z')

    #Publish the message
    client.publish(status_topic, json.dumps(working_json))
    #print("Message published")
    print("Message published: " + json.dumps(working_json))
    # Sleep a time until we do it over again
    time.sleep(10)  # Sleep for 10 seconds
