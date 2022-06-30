from typing import List

from models import State


def read_new_data() -> List[State]:
    states = []
    states.append(State(altitude=100))
    states.append(State(altitude=540))
    states.append(State(altitude=750))
    states.append(State(altitude=250, longitude=12.452, latitude=54.124))
    states.append(State(latitude=41.8257, longitude=39.9468))
    states.append(State(latitude=47.0161, longitude=26.1547))
    states.append(State(latitude=47.3557, longitude=24.9239))
    states.append(State(latitude=47.6735, longitude=23.7037))
    states.append(State(latitude=49.2036, longitude=16.5827))
    states.append(State(voltage_battery=451, voltage_capacitor=123))
    states.append(State(voltage_battery=200, voltage_capacitor=564))
    states.append(State(voltage_battery=83, voltage_capacitor=800))
    return states
