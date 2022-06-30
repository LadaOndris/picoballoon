import json
import logging
from struct import pack, unpack
from typing import Tuple

import numpy as np
import paho.mqtt.client as mqtt

from database import init_db
from models import insert_states, State


class Payload:

    def __init__(self, temperature: int, pressure: int, vbattery: int, vcapacitor: int,
                 read_attempts: int, init_attempts: int):
        self.temperature = temperature
        self.pressure = pressure
        self.vbattery = vbattery
        self.vcapacitor = vcapacitor
        self.read_attempts = read_attempts
        self.init_attempts = init_attempts

    def __repr__(self):
        return f'<Payload(pressure={self.pressure}, ' \
               f'vbattery={self.vbattery}, vcapacitor={self.vcapacitor})>'


def save_to_db(payload: Payload, position: Tuple, altitude: int) -> None:
    state = State(latitude=position[0], longitude=position[1],
                  voltage_capacitor=payload.vcapacitor,
                  voltage_battery=payload.vbattery,
                  pressure=payload.pressure,
                  temperature=payload.temperature,
                  init_attempts=payload.init_attempts,
                  read_attempts=payload.read_attempts,
                  altitude=altitude)
    insert_states([state])


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
    arg_names = ['temperature', 'pressure', 'vbattery', 'vcapacitor', 'read_attempts', 'init_attempts']
    payload_args = {}
    for arg_name in arg_names:
        payload_args[arg_name] = decoded_payload_json[arg_name]

    # latitude = reinterpret_int_as_float(latitude)
    # longitude = reinterpret_int_as_float(longitude)

    return Payload(**payload_args)


def triangulate_position(gateways_info) -> Tuple:
    rssis = []
    latitudes = []
    longitudes = []

    for i, info in enumerate(gateways_info):
        if 'location' in info:
            rssis.append(int(info['rssi']))
            latitudes.append(float(info['location']['latitude']))
            longitudes.append(float(info['location']['longitude']))

    if len(rssis) == 0:
        return None, None

    rssis = np.array(rssis, dtype=int)
    latitudes = np.array(latitudes, dtype=float)
    longitudes = np.array(longitudes, dtype=float)

    weights = compute_weights_from_dbms(rssis)
    latitude = np.sum(latitudes * weights)
    longitude = np.sum(longitudes * weights)
    return latitude, longitude


def compute_weights_from_dbms(dbms: np.ndarray) -> np.ndarray:
    # dBm to signal power
    dbms_div = dbms / 10
    power = 10 ** dbms_div

    # Normalize to create weights
    power_sum = np.sum(power)
    weights = power / power_sum

    return weights


def pressure_to_altitude(pressure: int) -> int:
    return 0


def on_message(mqttc, obj, msg):
    logging.info("Received message. Decoding content...")

    x = json.loads(msg.payload.decode('utf-8'))
    uplink_message = x['uplink_message']
    decoded_payload = uplink_message['decoded_payload']
    gateways_info = uplink_message['rx_metadata']

    payload: Payload = read_payload(decoded_payload)
    position = triangulate_position(gateways_info)
    altitude = pressure_to_altitude(payload.pressure)
    save_to_db(payload, position, altitude)


def on_publish(mosq, obj, mid):
    logging.info(f"Published: mid: {mid}")


def on_subscribe(mosq, obj, mid, granted_qos):
    logging.info(f"Subscribed: {mid} {granted_qos}")


if __name__ == "__main__":

    logging.basicConfig(filename='picoballoon_client.log',
                        filemode='a',
                        format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                        datefmt='%H:%M:%S',
                        level=logging.INFO)

    with open("config.json", "r") as config_file:
        config = json.load(config_file)['client']

    logging.info(f'Initializing database...')
    init_db()

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
        try:
            mqttc.loop()
        except Exception as e:
            logging.exception("Exception occured!")
