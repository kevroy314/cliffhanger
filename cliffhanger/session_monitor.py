"""This module contains asynchronous code which runs once on server start that monitors sessions for hourly bet resolution."""
import datetime
import os
import threading
import time

from sqlitedict import SqliteDict

from cliffhanger.database.session import Session
from cliffhanger.database.user import User
from cliffhanger.utils.globals import DATA_LOCATION

SCAN_INTERVAL = 5000


def _stats_thread_func():
    prev_time = datetime.datetime.now()
    while True:
        cur_time = datetime.datetime.now()
        db_path = os.path.join(DATA_LOCATION, 'db.sqlite')
        tables = SqliteDict(db_path).get_tablenames(db_path)
        resolve_party_bets = False
        if prev_time.hour != cur_time.hour:
            resolve_party_bets = True
        session_users = []
        session_ids = []
        for table in tables:
            if '_' not in table:
                session = Session(table)
                users = list(session.users.keys())
                session_users.append(users)
                session_ids.append(table)
        for session_id, usernames in zip(session_ids, session_users):
            bet_pools = {}
            for username in usernames:
                user = User(session_id, username)
                for bet in user.bets:
                    if bet.result == "Unresolved":
                        if bet.user not in bet_pools:
                            bet_pools[bet.user] = [(username, bet)]
                        else:
                            bet_pools[bet.user].append((username, bet))
            for bet_target in list(bet_pools.keys()):
                if bet_target == "party" and resolve_party_bets:
                    # find closest without going over and resolve bet
                    pass
                elif bet_target != "party":
                    # find closest and resolve bet
                    pass

        prev_time = cur_time
        time.sleep(SCAN_INTERVAL)


session_monitor_thread = threading.Thread(target=_stats_thread_func)
session_monitor_thread.start()
