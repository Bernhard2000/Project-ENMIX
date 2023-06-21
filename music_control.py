import spotipy
import random
from spotipy.oauth2 import SpotifyOAuth
from paho.mqtt import client as mqtt_client


broker = 'broker.hivemq.com'
port = 1883
client_id = f'musicControl-{random.randint(0, 100)}'
client_username = 'emqx'
client_password = 'public'
client: mqtt_client

topic_start = "15372648/enmix/controller/command/start"
topic_next = "15372648/enmix/controller/command/next"
topic_prev = "15372648/enmix/controller/command/previous"
topic_volume = "15372648/enmix/controller/command/volume"
topic_rickroll = "15372648/enmix/controller/command/rickroll"

sp_client_id="not stored in git :)"
sp_client_secret="not stored in git :)"
sp_redirect_uri="https://localhost:8888/callback"
sp_scope="user-modify-playback-state"
sp_volume=50

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=sp_client_id,
                                               client_secret=sp_client_secret,
                                               redirect_uri=sp_redirect_uri,
                                               scope=sp_scope))


def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client: mqtt_client, topic):
    def on_message(client, userdata, msg):
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        if msg.topic == topic_start:
            try:
                sp.pause_playback()
            except:
                try:
                    sp.start_playback()
                except:
                    print("error while toggling playback")
            print("start/stop")
        elif msg.topic == topic_next:
            sp.next_track()
            print("next")
        elif msg.topic == topic_prev:
            sp.previous_track()
            print("prev")
        elif msg.topic == topic_volume:
            global sp_volume
            sp_volume = sp_volume + int(msg.payload)
            sp_volume = max(sp_volume, 0)
            sp_volume = min(sp_volume, 100)
            sp.volume(sp_volume)
            print(f"volume change: {sp_volume}")
        elif msg.topic == topic_rickroll:
            sp.add_to_queue("4cOdK2wGLETKBW3PvgPWqT")
            sp.next_track()
            print(f"Rickroll time")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client, topic_start)
    subscribe(client, topic_next)
    subscribe(client, topic_prev)
    subscribe(client, topic_volume)
    subscribe(client, topic_rickroll)
    client.loop_forever()


if __name__ == '__main__':
    run()