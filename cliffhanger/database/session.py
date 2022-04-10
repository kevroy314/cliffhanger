from cliffhanger.database.user import User
from cliffhanger.utils.globals import data_location, drinks_cat_lut
from sqlitedict import SqliteDict
import string, random
import os
import pandas as pd
import plotly.express as px

class Session():
    def __init__(self, session_id):
        self.session_id = session_id
        self.session_db = SqliteDict(os.path.join(data_location, session_id), autocommit=True)
        self.users = {}
        
        if 'users' not in self.session_db:
            self.session_db['users'] = {}
        else:
            for username in self.session_db['users']:
                self.users[username] = User(self.session_id, username)

    def new_user(self, username):
        if username not in self.users:
            new_user = User(self.session_id, username)
            self.users[username] = new_user
            self.session_db['users'] = list(self.users.keys()) #session database only stores keys
            return new_user
        raise ValueError("Username taken in this session.")

    def extract_data_snapshot(self):
        event_data = []
        for username in list(self.users.keys()):
            user = User(self.session_id, username)
            for bac, dt, drinks, points in zip(user.bac_history,
                                               user.bac_history_datetimes,
                                               user.drink_description_checklist_history,
                                               user.points_history):
                event_data.append({'user': username, 'dt': dt, "bac": bac, "drinks": [drinks_cat_lut[d] for d in drinks], "points": points})

        df = pd.DataFrame(event_data)
        columns = ['user', 'dt', 'bac', 'drinks', 'points']
        for c in columns:
            if c not in df.columns:
                df[c] = []
        return df

    def create_session_graph(self):
        df = self.extract_data_snapshot()
        df = df.rename({'dt': 'Datetime', 'bac': 'BAC', 'user': "User"}, axis=1)
        return px.line(df, x='Datetime', y='BAC', color='User')
    
    def create_session_score_graph(self):
        df = self.extract_data_snapshot()
        df = df.rename({'dt': 'Datetime', 'points': 'Points', 'user': "User"}, axis=1)
        return px.line(df, x='Datetime', y='Points', color='User')

    @staticmethod
    def create_session():
        allowed_letters = string.ascii_lowercase.replace('i', '') \
                                                .replace('l', '') \
                                                .replace('o', '')
        allowed_digits = string.digits.replace("0", "") \
                                      .replace("1", "")
        session_id = ''.join(random.choices(allowed_letters + allowed_digits, k=8))
        return Session(session_id)

    @staticmethod
    def get_session(session_id):
        return Session(session_id)
    