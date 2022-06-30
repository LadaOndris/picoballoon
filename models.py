import logging
from datetime import datetime
from typing import List

from sqlalchemy import Column, DateTime, Float, Integer

from database import Base, db_session


class State(Base):
    __tablename__ = 'states'
    id = Column(Integer, primary_key=True)
    date_time = Column(DateTime, unique=True)
    height = Column(Integer)
    latitude = Column(Float)
    longitude = Column(Float)
    voltage_battery = Column(Integer)
    voltage_capacitor = Column(Integer)

    def __init__(self, date_time=None, height=None, latitude=None, longitude=None,
                 voltage_battery=None, voltage_capacitor=None):
        if date_time is None:
            date_time = datetime.now()
        self.date_time = date_time
        self.height = height
        self.latitude = latitude
        self.longitude = longitude
        self.voltage_battery = voltage_battery
        self.voltage_capacitor = voltage_capacitor

    def __repr__(self):
        datetime_formatted = self.date_time.strftime("%d/%m/%Y %H:%M:%S")
        return f'<State {datetime_formatted} at {self.height} m>'


def insert_states(states: List[State]) -> None:
    logging.debug(f'Inserting {len(states)} new states into the database.')
    for state in states:
        db_session.add(state)
    db_session.commit()


def query_all_states() -> List[State]:
    """
    Read all records from the database.
    :return: List of State instances.
    """
    states = State.query.all()
    logging.debug(f'Retrieved all {len(states)} states from the database.')
    return states
