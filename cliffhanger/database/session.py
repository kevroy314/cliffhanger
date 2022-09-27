"""This module defines the Session information and persists it."""
import os
import random
import string

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from sqlitedict import SqliteDict

from cliffhanger.database.user import User
from cliffhanger.utils.globals import (DATA_LOCATION, drinks_cat_lut)


class Session():
    """The Session object which defines and persists session propertise."""

    def __init__(self, session_id, create_if_not_exist=False):
        """Initialize a Session and create it if it doesn't exist and it should.

        Args:
            session_id (str): the session id
            create_if_not_exist (bool, optional): if True and the session is new, it is added to the DB and initialized. Defaults to True.

        Raises:
            KeyError: If create_if_not_exists is False and the session doesn't exist, a KeyError is raised.
        """
        session_id = session_id.lower()
        self.session_id = session_id
        db_path = os.path.join(DATA_LOCATION, 'db.sqlite')
        if not create_if_not_exist:
            if session_id not in SqliteDict(db_path).get_tablenames(db_path):
                raise KeyError(f"Tablename {session_id} does not exist and create_if_not_exists is False.")
        self.session_db = SqliteDict(db_path, tablename=session_id, autocommit=True)
        self.users = {}
        if 'users' not in self.session_db:
            self.session_db['users'] = {}
        else:
            for username in self.session_db['users']:
                self.users[username] = User(self.session_id, username, create_if_not_exist=True)

        if 'stats' not in self.session_db:
            self.stats = {}
        else:
            self.stats = self.session_db['stats']

    def set_stat(self, stat_key, stat_value):
        """Set and persist a stat key.

        Args:
            stat_key (str): a key to set
            stat_value (any): a value to set (must be set entirely)
        """
        self.stats[stat_key] = stat_value
        self.session_db['stats'] = self.stats

    def get_stat(self, stat_key):
        """Get a stat value from the key. Same as obj.stats[stat_key] .

        Args:
            stat_key (str): a stat key

        Returns:
            any: the stat object
        """
        return self.stats[stat_key]

    def new_user(self, username):
        """Create a new user if possible.

        Args:
            username (str): the username

        Raises:
            ValueError: Raised if the user already exists in this session.

        Returns:
            cliffhanger.database.user.User: the new User object
        """
        if username not in self.users:
            new_user = User(self.session_id, username, create_if_not_exist=True)
            self.users[username] = new_user
            self.session_db['users'] = list(self.users.keys())  # session database only stores keys
            return new_user
        raise ValueError("Username taken in this session.")

    def extract_data_snapshot(self):
        """Get a snapshot of the current user data in this session.

        Returns:
            pd.DataFrame: a Pandas DataFrame for this session's current state (and history)
        """
        event_data = []
        for username in list(self.users.keys()):
            user = User(self.session_id, username, create_if_not_exist=True)
            for bac, dt, drinks in zip(user.bac_history,
                                               user.bac_history_datetimes,
                                               user.drink_description_checklist_history):
                event_data.append({'user': username, 'dt': dt, "bac": bac, "drinks": [drinks_cat_lut[d] for d in drinks]})

        df = pd.DataFrame(event_data)
        columns = ['user', 'dt', 'bac', 'drinks']
        for c in columns:
            if c not in df.columns:
                df[c] = []
        return df

    def create_session_graph(self):
        """Create a graph figure for the session.

        Returns:
            go.Figure: a figure plotting the session BACs
        """
        df = self.extract_data_snapshot()

        user_dfs = df.groupby('user')
        mdf = pd.DataFrame()
        mdf['dt'] = df['dt'].unique()
        mdf = mdf.set_index('dt').sort_index()
        for username, udf in user_dfs:
            udf = udf.set_index("dt")
            mdf[username + '_bac'] = udf['bac']
        mdf = mdf.fillna(method="ffill").fillna(method="bfill")
        mdf = mdf.mean(axis=1).reset_index()
        mdf.columns = ["Datetime", "Party Average"]

        df = df.rename({'dt': 'Datetime', 'bac': 'BAC', 'user': "User"}, axis=1)
        fig = px.line(df, x='Datetime', y='BAC', color='User')
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0),
            xaxis=dict(title="Datetime"),
            yaxis=dict(title="BAC"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=300,
            legend=dict(
                title="User",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0
            )
        )
        fig.add_trace(go.Scatter(x=mdf['Datetime'], y=mdf['Party Average'], name='Party Average',
                                 line=dict(color='rgba(85, 111, 230, 0.5)', width=4, dash='dot'), mode='lines'))
        return fig

    @staticmethod
    def create_session():
        """Create a new random session id, initialize it, and return the object reference.

        Returns:
            cliffhanger.database.session.Session: the newly created Sesssion object
        """
        allowed_letters = string.ascii_lowercase.replace('i', '') \
                                                .replace('l', '') \
                                                .replace('o', '')
        allowed_digits = string.digits.replace("0", "") \
                                      .replace("1", "")
        session_id = ''.join(random.choices(allowed_letters + allowed_digits, k=8))
        return Session(session_id, create_if_not_exist=True)

    @staticmethod
    def get_session(session_id):
        """Get an existing session (will error if does not exist).

        Args:
            session_id (str): the session id string

        Returns:
            cliffhanger.database.session.Session: a session object
        """
        return Session(session_id, create_if_not_exist=False)
