"""This module contains asynchronous code which runs once on server start that monitors sessions for hourly updates."""
import datetime
import os
import threading
import time
import logging

import numpy as np

from sqlitedict import SqliteDict

from cliffhanger.database.session import Session
from cliffhanger.database.user import User
from cliffhanger.utils.globals import DATA_LOCATION

SCAN_INTERVAL = 5

def _stats_thread_func():
    # for change detection
    prev_time = datetime.datetime.now()
    prev_bac_updates = {}
    first_time = True
    while True:
        # track the start time
        cur_time = datetime.datetime.now()
        # connect to the database
        db_path = os.path.join(DATA_LOCATION, 'db.sqlite')
        tables = SqliteDict(db_path).get_tablenames(db_path)
        # populate a list of users in each session
        session_users = []
        session_ids = []
        for table in tables:
            if '_' not in table:
                session = Session(table)
                users = list(session.users.keys())
                session_users.append(users)
                session_ids.append(table)
        # calculate if this update crosses an hour threshold
        hour_update_trigger = first_time
        first_time = False
        if prev_time.hour != cur_time.hour:
            hour_update_trigger = True
        if hour_update_trigger:
            # iterate through the sessions
            for session_id, usernames in zip(session_ids, session_users):
                bac_sum = 0
                max_bac = -1
                for username in usernames:
                    # get the user data and sum
                    user = User(session_id, username)
                    if user.latest_bac != "Undefined":
                        latest_bac = float(user.latest_bac)
                        if latest_bac > max_bac:
                            max_bac = latest_bac
                        bac_sum += latest_bac
                party_bac = float(0)
                if len(usernames) > 0:
                    party_bac = bac_sum / len(usernames)
                logging.info(f"Setting averages for session {session_id}")
                session = Session(session_id)
                try:
                    party_average = session.get_stat('party_average')
                except KeyError:
                    party_average = float(0)
                try:
                    party_next_bet = session.get_stat('party_next_bet')
                except KeyError:
                    party_next_bet = float(-1)
                session.set_stat('prev_party_average', party_average)
                session.set_stat('prev_party_next_bet', party_next_bet)
                session.set_stat('party_average', party_bac)
                session.set_stat('party_next_bet', np.random.uniform(low=0, high=max_bac, size=(1,))[0])
            # Set session party average bet latest
            # Set session random number latest and log previous for visualization
        prev_time = cur_time
        time.sleep(SCAN_INTERVAL)


session_monitor_thread = threading.Thread(target=_stats_thread_func)
session_monitor_thread.start()