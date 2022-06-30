import logging
from typing import List

from flask import Flask, render_template

from data import update_database
from database import db_session, init_db
from models import query_all_states, State

logging.basicConfig(filename='picoballoon.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)
logging.info("Setting up logger.")

app = Flask(__name__)
init_db()


@app.route('/')
def index():
    logging.debug(f'Handling request: index.')
    last_update = update_database()
    states = query_all_states()
    last_update_string = format_last_update(last_update)
    return render_template('index.html', lastUpdateDateTime=last_update_string, states=states)


@app.route('/data')
def data():
    logging.debug(f'Handling request: data.')
    last_update = update_database()
    states = query_all_states()
    last_update_string = format_last_update(last_update)
    return render_template('data.html', lastUpdateDateTime=last_update_string, states=states)


def format_last_update(last_update) -> str:
    return last_update.strftime("%d/%m/%Y %H:%M:%S")


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@app.template_filter('lastposition')
def last_valid_position_filter(list: List[State]) -> State:
    for state in reversed(list):
        if state.latitude is not None and state.longitude is not None:
            return state
    return State(latitude=0, longitude=0)


if __name__ == '__main__':
    app.run()
