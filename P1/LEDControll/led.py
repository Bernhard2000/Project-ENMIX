import random

from paho.mqtt import client as mqtt_client

from sense_hat import SenseHat


broker = 'broker.hivemq.com'
port = 1883
topic_start = "15372648/enmix/controller/command/start"
topic_next = "15372648/enmix/controller/command/next"
topic_prev = "15372648/enmix/controller/command/previous"

topic_volume_db = "15372648/enmix/player/volume/feedback"
topic_volume_lvl = "15372648/enmix/player/volume/level"

# Generate a Client ID with the subscribe prefix.
client_id = f'subscribe-{random.randint(0, 100)}'


# username = 'emqx'
# password = 'public'

s = SenseHat()


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
            s.set_pixels(start_stop())
            print("start/stop")
        elif msg.topic == topic_next:
            s.set_pixels(next_track())
            print("next")
        elif msg.topic == topic_prev:
            s.set_pixels(prev_track())
            print("prev")
        elif msg.topic == topic_volume_db:
            print("db: ", msg.payload.decode())
        elif msg.topic == topic_volume_lvl:
            print("lvl: ", msg.payload.decode())
            if int(msg.payload.decode()) <= 12:
                s.set_pixels(volume_lvl1())
                print("lvl 1")
            elif 25 >= int(msg.payload.decode()) > 12:
                s.set_pixels(volume_lvl2())
                print("lvl 2")
            elif 37 >= int(msg.payload.decode()) > 25:
                s.set_pixels(volume_lvl3())
                print("lvl 3")
            elif 49 >= int(msg.payload.decode()) > 37:
                s.set_pixels(volume_lvl4())
                print("lvl 4")
            elif 61 >= int(msg.payload.decode()) > 49:
                s.set_pixels(volume_lvl5())
                print("lvl 5")
            elif 73 >= int(msg.payload.decode()) > 61:
                s.set_pixels(volume_lvl6())
                print("lvl 6")
            elif 85 >= int(msg.payload.decode()) > 73:
                s.set_pixels(volume_lvl7())
                print("lvl 7")
            else:
                s.set_pixels(volume_lvl8())
                print("lvl 8")

    client.subscribe(topic)
    client.on_message = on_message


def run():
    client = connect_mqtt()
    subscribe(client, topic_start)
    subscribe(client, topic_next)
    subscribe(client, topic_prev)
    subscribe(client, topic_volume_db)
    subscribe(client, topic_volume_lvl)
    client.loop_forever()


if __name__ == '__main__':
    run()

green = (0, 255, 0)
yellow = (255, 255, 0)
red = (255, 0, 0)
white = (255, 255, 255)
nothing = (0, 0, 0)


def start_stop():
    W = white
    O = nothing
    logo = [
        O, O, O, O, O, O, O, O,
        O, W, W, O, W, O, O, O,
        O, W, W, O, W, W, O, O,
        O, W, W, O, W, W, W, O,
        O, W, W, O, W, W, W, O,
        O, W, W, O, W, W, O, O,
        O, W, W, O, W, O, O, O,
        O, O, O, O, O, O, O, O,
    ]
    return logo


def next_track():
    W = white
    O = nothing
    logo = [
        O, O, O, O, O, O, O, O,
        O, W, O, O, W, O, O, O,
        O, O, W, O, O, W, O, O,
        O, O, O, W, O, O, W, O,
        O, O, O, W, O, O, W, O,
        O, O, W, O, O, W, O, O,
        O, W, O, O, W, O, O, O,
        O, O, O, O, O, O, O, O,
    ]
    return logo


def prev_track():
    W = white
    O = nothing
    logo = [
        O, O, O, O, O, O, O, O,
        O, O, O, W, O, O, W, O,
        O, O, W, O, O, W, O, O,
        O, W, O, O, W, O, O, O,
        O, W, O, O, W, O, O, O,
        O, O, W, O, O, W, O, O,
        O, O, O, W, O, O, W, O,
        O, O, O, O, O, O, O, O,
    ]
    return logo


def volume_lvl1():
    G = green
    O = nothing
    logo = [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        G, O, O, O, O, O, O, O,
    ]
    return logo


def volume_lvl2():
    G = green
    O = nothing
    logo = [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, G, O, O, O, O, O, O,
        G, G, O, O, O, O, O, O,
    ]
    return logo


def volume_lvl3():
    G = green
    O = nothing
    logo = [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, G, O, O, O, O, O,
        O, G, G, O, O, O, O, O,
        G, G, G, O, O, O, O, O,
    ]
    return logo


def volume_lvl4():
    G = green
    Y = yellow
    O = nothing
    logo = [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, Y, O, O, O, O,
        O, O, G, Y, O, O, O, O,
        O, G, G, Y, O, O, O, O,
        G, G, G, Y, O, O, O, O,
    ]
    return logo


def volume_lvl5():
    G = green
    Y = yellow
    O = nothing
    logo = [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, Y, O, O, O,
        O, O, O, Y, Y, O, O, O,
        O, O, G, Y, Y, O, O, O,
        O, G, G, Y, Y, O, O, O,
        G, G, G, Y, Y, O, O, O,
    ]
    return logo


def volume_lvl6():
    G = green
    Y = yellow
    O = nothing
    logo = [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, Y, O, O,
        O, O, O, O, Y, Y, O, O,
        O, O, O, Y, Y, Y, O, O,
        O, O, G, Y, Y, Y, O, O,
        O, G, G, Y, Y, Y, O, O,
        G, G, G, Y, Y, Y, O, O,
    ]
    return logo


def volume_lvl7():
    G = green
    Y = yellow
    R = red
    O = nothing
    logo = [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, R, O,
        O, O, O, O, O, Y, R, O,
        O, O, O, O, Y, Y, R, O,
        O, O, O, Y, Y, Y, R, O,
        O, O, G, Y, Y, Y, R, O,
        O, G, G, Y, Y, Y, R, O,
        G, G, G, Y, Y, Y, R, O,
    ]
    return logo


def volume_lvl8():
    G = green
    Y = yellow
    R = red
    O = nothing
    logo = [
        O, O, O, O, O, O, O, R,
        O, O, O, O, O, O, R, R,
        O, O, O, O, O, Y, R, R,
        O, O, O, O, Y, Y, R, R,
        O, O, O, Y, Y, Y, R, R,
        O, O, G, Y, Y, Y, R, R,
        O, G, G, Y, Y, Y, R, R,
        G, G, G, Y, Y, Y, R, R,
    ]
    return logo
