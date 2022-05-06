"""This module defines the User properties and methods for persisting user data."""
from datetime import datetime
from cliffhanger.point_rules import submit_new_bac_points, timer_use_points
from cliffhanger.utils.formats import datetime_string_format
from cliffhanger.utils.globals import data_location, drinks_cat_lut, drinks_color_lut
import plotly.express as px
import plotly.graph_objs as go
from sqlitedict import SqliteDict
import uuid
import os
import numpy as np
import pandas as pd


class User():
    """An object which persists and returns user data."""

    def __init__(self, session_id, username, create_if_not_exist=False):
        """Get the current user data state, creating it if requested and it doesn't exist.

        Args:
            session_id (str): the session id
            username (str): the username for this session
            create_if_not_exist (bool, optional): if True and the user is new, it is added to the DB and initialized. Defaults to True.

        Raises:
            KeyError: If create_if_not_exists is False and the user doesn't exist, a KeyError is raised.
        """
        session_id = session_id.lower()
        tablename = session_id + "_" + username
        db_path = os.path.join(data_location, 'db.sqlite')
        if not create_if_not_exist:
            if tablename not in SqliteDict(db_path).get_tablenames(db_path):
                raise KeyError(f"Tablename {session_id} does not exist and create_if_not_exists is False.")
        self.user_db = SqliteDict(db_path, tablename=tablename, autocommit=True)
        if 'user' not in self.user_db:
            self.username = username
            self.bac_history = []
            self.bac_history_datetimes = []
            self.drink_description_checklist_history = []
            self.latest_bac = "Undefined"
            self.last_update = datetime.now().strftime(datetime_string_format)
            self.points = 0
            self.points_history = []
            self.user_secret = str(uuid.uuid4())
            self.bets = []
            self.user_db['user'] = self.serialize()
        else:
            self.load_from_serialized(self.user_db['user'])

    def serialize(self):
        """Serialize the user data to a dictionary."""
        return {
            'username': self.username,
            'bac_history': self.bac_history,
            'bac_history_datetimes': self.bac_history_datetimes,
            'drink_description_checklist_history': self.drink_description_checklist_history,
            'latest_bac': self.latest_bac,
            'last_update': self.last_update,
            'points': self.points,
            'points_history': self.points_history,
            'user_secret': self.user_secret,
            'bets': self.bets
        }

    def add_bet(self, bet):
        """Add a bet to the user and persist it.

        Args:
            bet (cliffhanger.pages.bets.Bet): a Bet object
        """
        self.bets.append(bet)
        self.user_db['user'] = self.serialize()

    def load_from_serialized(self, serialized_dict):
        """Load data from a serialized dictionary into THIS object.

        Args:
            serialized_dict (dict): a serialized dictionary loaded from a persistence layer
        """
        for key in serialized_dict:
            setattr(self, key, serialized_dict[key])

    def update_bac(self, new_bac, timer_value=None, drink_description_checklist=None):
        """Update the BAC of this user. Note, points are applied in this function.

        Args:
            new_bac (float): the new BAC for the user
            timer_value (float, optional): the value of the timer object on submission (for bonus points). Defaults to None.
            drink_description_checklist (list, optional): the list of drink types the user had during the last period. Defaults to None.
        """
        now = datetime.now()
        self.bac_history.append(float(new_bac))
        self.bac_history_datetimes.append(now)
        self.drink_description_checklist_history.append(drink_description_checklist)
        self.latest_bac = str(new_bac)
        self.last_update = now.strftime(datetime_string_format)

        # SCORING

        def is_in_same_hour(dt0, dt1):
            root_dt = datetime(2022, 4, 9, 0, 0, 0, 0)
            dt0_delta = dt0 - root_dt
            dt1_delta = dt1 - root_dt
            dt0_total_seconds = dt0_delta.total_seconds()
            dt1_total_seconds = dt1_delta.total_seconds()
            dt0_hour = dt0_total_seconds - (dt0_total_seconds % 3600)
            dt1_hour = dt1_total_seconds - (dt1_total_seconds % 3600)
            return dt0_hour != dt1_hour

        # award points for BAC entry if it is the first entry or the first entry in this hour
        if len(self.bac_history_datetimes) == 1 or \
                is_in_same_hour(self.bac_history_datetimes[-2], self.bac_history_datetimes[-1]):
            self.points += submit_new_bac_points
            # If they used the timer and it's within 30 seconds of 0, bonus points!
            if timer_value is not None and timer_value <= 30:
                self.points += timer_use_points
        self.points_history.append(self.points)
        self.user_db['user'] = self.serialize()

    def get_user_graph(self, n_points=1000):
        """Get the graph of the users data.

        Args:
            n_points (int, optional): the number of points to display (for multicoloring). Defaults to 1000.

        Returns:
            go.Figure: a figure object to display
        """
        if len(self.bac_history) > 1:
            x = self.bac_history_datetimes
            y = self.bac_history
            # Disregard first entry as it doesn't have a line segment
            cats = self.drink_description_checklist_history[1:]

            xx, yy, cc = [], [], []
            for idx, ((x0, x1), (y0, y1)) in enumerate(zip(zip(x[:-1], x[1:]), zip(y[:-1], y[1:]))):
                points = int(n_points * ((x1 - x0) / (max(x) - min(x))))
                xx.extend(pd.to_datetime(np.linspace(pd.Timestamp(x0).value, pd.Timestamp(x1).value, points)))
                yy.extend(np.linspace(y0, y1, points))
                if len(cats[idx]) > 0:
                    colors = [val for val in list(cats[idx]) for _ in range(int(points / len(cats[idx])))]
                    colors = colors + [cats[idx][-1]] * (points - len(colors))
                else:
                    colors = [1 for _ in range(points)]
                cc.extend(colors)

            cc = [drinks_cat_lut[e] if e in drinks_cat_lut else e for e in cc]

            fig = px.scatter(x=xx, y=yy, color=cc,
                             color_discrete_map=drinks_color_lut)
        elif len(self.bac_history) == 1:
            fig = px.scatter(x=self.bac_history_datetimes, y=self.bac_history,
                             color_discrete_map=drinks_color_lut)
        else:
            fig = go.Figure()
        fig.update_layout(
            margin=dict(l=0, r=0, b=0, t=0,),
            xaxis=dict(title="Datetime"),
            yaxis=dict(title="BAC"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(
                title="Alcohol Type",
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="left",
                x=0
            ),
            height=300,
        )
        return fig
