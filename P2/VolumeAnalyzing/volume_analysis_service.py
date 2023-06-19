import time
import pyaudio
import audioop
import wave
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
volume_threshold = 0.05
cycle_sleep = 50   # Sleep time in ms

# Mic in stream
form_1 = pyaudio.paInt16 # 16-bit resolution
chans = 1 # 1 channel
sample_rate = 44100 # 44.1kHz sampling rate
chunk = 4096 # 2^12 samples for buffer
dev_index = 2 # device index found by p.get_device_info_by_index(ii)
stream = None
sample_seconds = 0.2


def meaure_volume() -> float:
    for i in range(0, int(sample_rate / chunk * sample_seconds)):
        data = stream.read(chunk)
        rms = audioop.rms(data, 2)    # calculate the volume
    return rms

def publish_volume_value(volume: float):
    result = client.publish(topic_volume_feedback, volume)
    # result: [0, 1]
    status = result[0]
    if status != 0:
        print(f"Failed to send message to topic {topic_volume_feedback}")
    return

def start_working_cycle():
    last_sent_volume = 0
    while not stop_cycle:
        volume = meaure_volume()
        # if changed publish
        if abs(volume-last_sent_volume) > volume_threshold:
            publish_volume_value(volume)
            last_sent_volume = volume
        time.sleep(cycle_sleep)
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
    # Make Mqtt Subscriptions
    # ...
    return 

def init_audio_stream():
    # create pyaudio instantiation
    audio = pyaudio.PyAudio() 
    # create pyaudio stream
    global stream
    stream = audio.open(format = form_1,rate = sample_rate,channels = chans, \
                    input_device_index = dev_index,input = True, \
                    frames_per_buffer=chunk)
    return

def init():
    init_mqtt_client
    init_audio_stream()
    start_working_cycle()
    stream.close()
    return

if __name__ == '__main__':
    init()
