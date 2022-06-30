from datetime import datetime
import ttn_source
import models
import logging

last_update = datetime.now()
update_interval_secs = 1 * 60  # 10 minutes
update_after_interval = False


def _secs_from_last_update() -> int:
    time_now = datetime.now()
    passed_interval_secs = (time_now - last_update).seconds
    return passed_interval_secs


def _should_update_database() -> bool:
    passed_interval_secs = _secs_from_last_update()
    interval_has_passed = passed_interval_secs >= update_interval_secs
    return (update_after_interval and interval_has_passed) or (not update_after_interval)


def update_database():
    logging.debug(f'Checking whether to update database.')
    global last_update
    should_update = _should_update_database()
    if should_update:
        logging.debug(f'Updating database.')
        last_update = datetime.now()
        new_data = ttn_source.read_new_data()
        models.insert_states(new_data)
    return last_update