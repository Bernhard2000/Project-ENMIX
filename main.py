import math
import random
import time

import cv2
import mediapipe as mp
import types

from paho.mqtt import client as mqtt_client

TOPIC_START = "15372648/enmix/controller/command/start"
TOPIC_NEXT = "15372648/enmix/controller/command/next"
TOPIC_PREVIOUS = "15372648/enmix/controller/command/previous"
TOPIC_VOLUME = "15372648/enmix/controller/command/volume"
TOPIC_RICKROLL = "15372648/enmix/controller/command/rickroll"

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

l = mp.solutions.hands.HandLandmark
indexfinger = types.SimpleNamespace()
indexfinger.touching = False
indexfinger.touchStart = 0
indexfinger.touchCounter = 0
indexfinger.lastTouch = 0
indexfinger.touchRegistered = 0
volume = 50


broker = "broker.hivemq.com"
port = 1883
client_id = f'python-mqtt-{random.randint(0, 1000)}'
# username = 'emqx'
# password = 'public'


def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    # Set Connecting Client ID
    client = mqtt_client.Client(client_id)
    # client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

FIRST_RECONNECT_DELAY = 1
RECONNECT_RATE = 2
MAX_RECONNECT_COUNT = 12
MAX_RECONNECT_DELAY = 60

def on_disconnect(client, userdata, rc):
    print("Disconnected with result code: %s", rc)
    reconnect_count, reconnect_delay = 0, FIRST_RECONNECT_DELAY
    while reconnect_count < MAX_RECONNECT_COUNT:
        time.sleep(reconnect_delay)

        try:
            client.reconnect()
            print("Reconnected successfully")
            return
        except Exception as err:
            print("Reconnect failed: %s", err)
        reconnect_delay *= RECONNECT_RATE
        reconnect_delay = min(reconnect_delay, MAX_RECONNECT_DELAY)
        reconnect_count += 1
    print("Reconnect failed after %s attempts. Exiting...", reconnect_count)

def publish(client):
    msg_count = 1
    while True:
        time.sleep(1)
        msg = f"messages: {msg_count}"
        result = client.publish(topic, msg)
        # result: [0, 1]
        status = result[0]
        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")
        msg_count += 1
        if msg_count > 5:
            break

client = connect_mqtt()
client.on_disconnect = on_disconnect
client.loop_start()




cap = cv2.VideoCapture("http://10.0.0.174:8000/stream.mjpeg")
with mp_hands.Hands(static_image_mode=0, model_complexity=0, min_detection_confidence=0.7, min_tracking_confidence=0.7, max_num_hands=1) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_id, hand_landmarks in enumerate(results.multi_hand_landmarks):
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

                list = []
                for id, pt in enumerate(hand_landmarks.landmark):
                    x = int(pt.x * 768)
                    y = int(pt.y * 576)
                    z = int(pt.z * 768)
                    list.append([id, x, y, z])
                a = list
                p = [a[l.INDEX_FINGER_TIP][1], a[l.INDEX_FINGER_TIP][2], a[l.INDEX_FINGER_TIP][3]]
                q = [a[l.THUMB_TIP][1], a[l.THUMB_TIP][2], a[l.THUMB_TIP][3]]
                t = [a[l.INDEX_FINGER_MCP][1], a[l.INDEX_FINGER_MCP][2], a[l.INDEX_FINGER_MCP][3]]
                u = [a[l.WRIST][1], a[l.WRIST][2], a[l.WRIST][3]]
                if math.dist(p, q) < (math.dist(t, u)/10 + 10):
                    if not indexfinger.touching:
                        indexfinger.touching = True
                        oldvolume = volume
                        indexfinger.startY = a[l.INDEX_FINGER_TIP][2]
                        indexfinger.touchStart = time.time_ns()
                        indexfinger.touchCounter = indexfinger.touchCounter + 1
                        print(indexfinger.touchCounter)

                    touchTime = time.time_ns() - indexfinger.touchStart
                    indexfinger.lastTouch = time.time_ns()
                    if touchTime > 300000000:
                        #volume = oldvolume + (-0.1 * (a[l.INDEX_FINGER_TIP][2] - indexfinger.startY))
                        #if volume < 0:
                        #    volume = 0
                        #if volume > 100:
                        #    volume = 100
                        volume = -0.05 * (a[l.INDEX_FINGER_TIP][2] - indexfinger.startY)
                        result = client.publish(TOPIC_VOLUME, str(int(volume)))
                        # result: [0, 1]
                        status = result[0]
                        if status != 0:
                            print(f"Failed to send message to topic {TOPIC_VOLUME}")
                        indexfinger.touchCounter = 0
                        print("Change volume: " + str(int(volume)))

                else:
                    indexfinger.touching = False
                    if time.time_ns() - indexfinger.lastTouch > 1000000000 and indexfinger.touchCounter > 0:
                        topic = None
                        if indexfinger.touchCounter == 1:
                            topic = TOPIC_START
                            print("Start/Stop")
                        if indexfinger.touchCounter == 2:
                            topic = TOPIC_NEXT
                            print("Next Track")
                        if indexfinger.touchCounter == 3:
                            topic = TOPIC_PREVIOUS
                            print("Previous Track")
                        if indexfinger.touchCounter == 4:
                            topic = TOPIC_RICKROLL
                            print("Rickroll")

                        if topic is not None:
                            result = client.publish(topic=topic, payload="")
                            # result: [0, 1]
                            status = result[0]
                            if status != 0:
                                print(f"Failed to send message to topic {topic}")
                        indexfinger.touchCounter = 0

        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
client.loop_stop()
