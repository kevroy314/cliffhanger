from datetime import datetime
from cliffhanger.point_rules import submit_new_bac_points, timer_use_points
from cliffhanger.utils.formats import datetime_string_format
from cliffhanger.utils.globals import data_location
import plotly.express as px
import plotly.graph_objs as go
from sqlitedict import SqliteDict
import uuid, os
import numpy as np
import pandas as pd

class User():
    def __init__(self, session_id, username):
        self.user_db = SqliteDict(os.path.join(data_location, session_id+"_"+username), autocommit=True)
        if 'user' not in self.user_db:
            self.username = username
            self.bac_history = []
            self.bac_history_datetimes = []
            self.drink_description_checklist_history = []
            self.latest_bac = "Undefined"
            self.last_update = datetime.now().strftime(datetime_string_format)
            self.points = 0
            self.user_secret = str(uuid.uuid4())
            self.user_db['user'] = self.serialize()
        else:
            self.load_from_serialized(self.user_db['user'])

    def serialize(self):
        return {
            'username': self.username,
            'bac_history': self.bac_history,
            'bac_history_datetimes': self.bac_history_datetimes,
            'drink_description_checklist_history': self.drink_description_checklist_history,
            'latest_bac': self.latest_bac,
            'last_update': self.last_update,
            'points': self.points,
            'user_secret': self.user_secret,
        }

    def load_from_serialized(self, serialized_dict):
        for key in serialized_dict:
            setattr(self, key, serialized_dict[key])

    def update_bac(self, new_bac, timer_value=None, drink_description_checklist=None):
        now = datetime.now()
        self.bac_history.append(float(new_bac))
        self.bac_history_datetimes.append(now)
        self.drink_description_checklist_history.append(drink_description_checklist)
        self.latest_bac = str(new_bac)
        self.last_update = now.strftime(datetime_string_format)
        def is_in_same_hour(dt0, dt1):
            root_dt = datetime(2022, 4, 9, 0, 0, 0, 0)
            dt0_delta = dt0 - root_dt
            dt1_delta = dt1 - root_dt
            dt0_total_seconds = dt0_delta.total_seconds()
            dt1_total_seconds = dt1_delta.total_seconds()
            dt0_hour = dt0_total_seconds - (dt0_total_seconds % 3600)
            dt1_hour = dt1_total_seconds - (dt1_total_seconds % 3600)
            return dt0_hour != dt1_hour

        strip_total_seconds_to_hour = lambda total_seconds: total_seconds - (total_seconds % 3600)

        # award points for BAC entry if it is the first entry or the first entry in this hour
        if len(self.bac_history_datetimes) == 1 or \
            is_in_same_hour(self.bac_history_datetimes[-2], self.bac_history_datetimes[-1]):
            self.points += submit_new_bac_points
            # If they used the timer and it's within 30 seconds of 0, bonus points!
            if timer_value is not None and timer_value <= 30: 
                self.points += timer_use_points
        self.user_db['user'] = self.serialize()

    def get_user_graph(self, n_points=1000):
        if len(self.bac_history) > 1: 
            x = self.bac_history_datetimes
            y = self.bac_history
            # Disregard first entry as it doesn't have a line segment
            cats = self.drink_description_checklist_history[1:]

            cat_lut = {
                1: "Nothing",
                2: "Beer",
                3: "Wine",
                4: "Liquor (Drinks)",
                5: "Liquor (Shots)"
            }
            color_lut = {
                "Nothing": "#0F0E0E",
                "Beer": "#f28e1c",
                "Wine": "#BA091E",
                "Liquor (Drinks)": "#ADD8E6",
                "Liquor (Shots)": "#2364AA"
            }

            possible_cats = len(cat_lut)

            xx, yy, cc = [], [], []
            for idx, ((x0, x1), (y0, y1)) in enumerate(zip(zip(x[:-1], x[1:]), zip(y[:-1], y[1:]))):
                points = int(n_points*((x1 - x0)/(max(x) - min(x))))
                xxe = pd.to_datetime(np.linspace(pd.Timestamp(x0).value, pd.Timestamp(x1).value, points))
                xx.extend(pd.to_datetime(np.linspace(pd.Timestamp(x0).value, pd.Timestamp(x1).value, points)))
                yy.extend(np.linspace(y0, y1, points))
                if len(cats[idx]) > 0:
                    colors = [val for val in list(cats[idx]) for _ in range(int(points/len(cats[idx])))]
                    colors = colors + [cats[idx][-1]]*(points - len(colors))
                else:
                    colors = [1 for _ in range(points)]
                cc.extend(colors)
                
            cc = [cat_lut[e] if e in cat_lut else e for e in cc]

            fig = px.scatter(x=xx, y=yy, color=cc,
                            color_discrete_map=color_lut)
            fig.update_layout(margin=dict(l=0, r=0, b=0, t=0,), xaxis=dict(title="Datetime"), yaxis=dict(title="BAC"))
            return fig
        else:
            layout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0), xaxis=dict(title="Datetime"), yaxis=dict(title="BAC"))
            fig = dict(layout=layout)
            return fig