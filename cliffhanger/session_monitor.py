"""This module contains asynchronous code which runs once on server start that monitors sessions for hourly bet resolution."""
import datetime
import os
import threading
import time

import numpy as np

from sqlitedict import SqliteDict

from cliffhanger.database.session import Session
from cliffhanger.database.user import User
from cliffhanger.utils.globals import DATA_LOCATION

SCAN_INTERVAL = 5


def _calculate_winners_and_losers(actual, bets, rule):
    assert rule in ["player", "party"], "rule must be player or party"
    bet_targets = np.array([bet.target for bet in bets])
    if rule == "player":
        # absolute rule applies
        dists = np.abs(actual - bet_targets)
        winner_mask = dists == dists.min()
    elif rule == "party":
        # closest without going over rule applies
        dists = actual - bet_targets
        winner_mask = np.logical_and(dists > 0, dists == np.abs(dists).min())
    winners = np.argwhere(winner_mask).flatten()
    losers = np.argwhere(np.logical_not(winner_mask)).flatten()
    return winners, losers


def _resolve_bets(session_id, bets, rule, actual):
    print("party bet")
    winners, losers = _calculate_winners_and_losers(actual, bets, rule=rule)
    loser_points = 0
    for loser in losers:
        username, bet = bets[loser]
        loser_points += bet.value
        User(session_id, username).resolve_bet_as_loss(bet)
    pot_split = np.floor(loser_points / np.sum(winners))
    for winner in winners:
        username, bet = bets[winner]
        User(session_id, username).resolve_bet_as_win(bet, pot_split)


def _stats_thread_func():
    # for change detection
    prev_time = datetime.datetime.now()
    prev_bac_updates = {}
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
        # calculate if this update is the first of the hour for party bates
        resolve_party_bets = False
        if prev_time.hour != cur_time.hour:
            resolve_party_bets = True
        # transpose the betting data for each session, creating a bet pool, and populate triggers for when a BAC blow occurs
        for session_id, usernames in zip(session_ids, session_users):
            bet_pools = {}  # maps user to bets made on that user
            user_triggers = {}  # maps user to if they blew since last update
            if session_id not in prev_bac_updates:
                prev_bac_updates[session_id] = {}  # default value to avoid key errors
            bac_sum = 0
            for username in usernames:
                # get the user data and default to no trigger
                user = User(session_id, username)
                bac_sum += user.latest_bac
                user_triggers[username] = False
                if username not in prev_bac_updates[session_id]:
                    prev_bac_updates[session_id][username] = None  # default value to avoid key errors
                # if the BAC value for a user is updated
                if prev_bac_updates[session_id][username] != user.last_update:
                    # if the previous state wasn't none (i.e. first iteration of the loop)
                    if prev_bac_updates[session_id][username] is not None:
                        user_triggers[username] = True  # trigger the bet logic for that user
                    prev_bac_updates[session_id][username] = user.last_update  # update the value for next iteration
                # iterate through the bets and populate the bet pool values (i.e. who bet on a given user)
                for bet in user.bets:
                    if bet.result == "Unresolved":
                        if bet.user not in bet_pools:
                            bet_pools[bet.user] = [(username, bet)]
                        else:
                            bet_pools[bet.user].append((username, bet))
            # now we have the key->value mappings describing who has bets on them and if those bets should be resolved this round
            # we also can tell if the party bets for the session should be resolved
            # we loop through all the bet targets and resolve them if the triggers are present
            party_bac = bac_sum / len(usernames)
            for bet_target in list(bet_pools.keys()):
                if bet_target is None and resolve_party_bets:
                    _resolve_bets(session_id, bet_pools[bet_target], "party", party_bac)
                elif bet_target is not None and user_triggers[bet_target]:
                    _resolve_bets(session_id, bet_pools[bet_target], "player", User(session_id, bet_target).latest_bac)
        prev_time = cur_time
        time.sleep(SCAN_INTERVAL)


session_monitor_thread = threading.Thread(target=_stats_thread_func)
session_monitor_thread.start()
