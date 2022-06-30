import json
import logging
from struct import pack, unpack

import paho.mqtt.client as mqtt


class Payload:

    def __init__(self, altitude: int, latitude: float, longitude: float, vbattery: int, vcapacitor: int):
        self.altitude = altitude
        self.latitude = latitude
        self.longitude = longitude
        self.vbattery = vbattery
        self.vcapacitor = vcapacitor

    def __repr__(self):
        return f'<Payload(altitude={self.altitude}, ' \
               f'latitude={self.latitude}, ' \
               f'longitude={self.longitude}, ' \
               f'vbattery={self.vbattery}, vcapacitor={self.vcapacitor})>'


def on_connect(mqttc, mosq, obj, rc):
    logging.info(f"Connected with result code: {rc}")
    logging.info(f"Subscribing to device: {device_id}")
    mqttc.subscribe(f'v3/+/devices/{device_id}/up')


def reinterpret_int_as_float(number) -> float:
    b = pack('i', number)
    number_float = unpack('f', b)[0]
    return number_float


def read_payload(decoded_payload_json) -> Payload:
    altitude = decoded_payload_json['altitude']
    latitude = decoded_payload_json['latitude']
    longitude = decoded_payload_json['longitude']
    vbattery = decoded_payload_json['vbattery']
    vcapactior = decoded_payload_json['vcapacitor']

    latitude = reinterpret_int_as_float(latitude)
    longitude = reinterpret_int_as_float(longitude)

    return Payload(altitude, latitude, longitude, vbattery, vcapactior)


def on_message(mqttc, obj, msg):
    logging.info("Received message. Decoding content...")

    x = json.loads(msg.payload.decode('utf-8'))
    uplink_message = x['uplink_message']
    frm_payload = uplink_message['frm_payload']
    decoded_payload = uplink_message['decoded_payload']

    payload: Payload = read_payload(decoded_payload)


def on_publish(mosq, obj, mid):
    logging.info(f"Published: mid: {mid}")


def on_subscribe(mosq, obj, mid, granted_qos):
    logging.info(f"Subscribed: {mid} {granted_qos}")


logging.basicConfig(filename='picoballoon.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

broker = 'eu1.cloud.thethings.network'
port = 1883
app_id = 'testv3tg'
device_id = 'eui-70b3d57ed0050aa7'
access_key = "NNSXS.UM2CNVLZH662W6JONDEEV5CDEB3RSUGPTEQUFJI.55KSB5VIOIBR3MKKAE34NYEUVH5KIIA5TNQGWBR7DTJ3MVRCCSFQ"

logging.info(f"Setting up MQTT client: app_id={app_id}, port={port}, broker={broker}")

mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

mqttc.username_pw_set(app_id, access_key)
mqttc.connect(broker, port)

logging.info(f"Starting infinite loop, waiting for messages...")
run = True
while run:
    mqttc.loop()
