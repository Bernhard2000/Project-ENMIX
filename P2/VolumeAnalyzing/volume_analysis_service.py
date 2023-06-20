import sounddevice as sd
import numpy as np
import random
from paho.mqtt import client as mqtt_client

stop_cycle = False

# MQTT
topic_volume_feedback = "15372648/enmix/player/volume/feedback"
mqtt_broker_url = "broker.hivemq.com"
mqtt_broker_port = 1883
client_id = f'volumeAnalyzer-{random.randint(0, 100)}'
client_username = 'emqx'
client_password = 'public'
client: mqtt_client

# Volume
volume_threshold = 12
last_sent_volume = 0


def publish_volume_value(volume: float):
    result = client.publish(topic_volume_feedback, volume)
    # result: [0, 1]
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {topic_volume_feedback}")
    return


def start_working_cycle():
    sd._terminate()
    sd._initialize()
    global last_sent_volume

    def check_volume(indata, outdata, frames, time, status):
        sd.sleep(50)
        global last_sent_volume
        try:
            volume = np.linalg.norm(indata)*10
            print(volume)
            if abs(volume-last_sent_volume) > volume_threshold:
                publish_volume_value(volume)
                last_sent_volume = volume
        except:
            print("ignore error")# error occured -- ignored

    with sd.Stream(callback=check_volume, finished_callback=start_working_cycle):
        sd.sleep(10000)
    return


def init_mqtt_client():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    global client
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(client_username, client_password)
    client.on_connect = on_connect
    client.connect(mqtt_broker_url, mqtt_broker_port)
    return


def init():
    init_mqtt_client()
    start_working_cycle()
    return


if __name__ == '__main__':
    print("test")
    init()
