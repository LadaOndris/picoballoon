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


def setup_on_connect_callback(device_id):
    def on_connect(mqttc, mosq, obj, rc):
        logging.info(f"Connected with result code: {rc}")
        logging.info(f"Subscribing to device: {device_id}")
        mqttc.subscribe(f'v3/+/devices/{device_id}/up')

    return on_connect


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


logging.basicConfig(filename='picoballoon_client.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

with open("config.json", "r") as config_file:
    config = json.load(config_file)['client']

logging.info(f'Setting up MQTT client: app_id={config["app_id"]}, broker={config["broker"]}, port={config["port"]}')

mqttc = mqtt.Client()
mqttc.on_connect = setup_on_connect_callback(config["device_id"])
mqttc.on_message = on_message
mqttc.on_publish = on_publish
mqttc.on_subscribe = on_subscribe

mqttc.username_pw_set(config["app_id"], config["access_key"])
mqttc.connect(config["broker"], config["port"])

logging.info(f"Starting infinite loop, waiting for messages...")
run = True
while run:
    mqttc.loop()
