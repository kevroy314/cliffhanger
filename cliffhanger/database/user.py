from datetime import datetime
from cliffhanger.point_rules import submit_new_bac_points
from cliffhanger.utils.formats import datetime_string_format
from cliffhanger.utils.globals import data_location
import plotly.express as px
import plotly.graph_objs as go
from sqlitedict import SqliteDict
import uuid, os

class User():
    def __init__(self, session_id, username):
        self.user_db = SqliteDict(os.path.join(data_location, session_id+"_"+username), autocommit=True)
        if 'user' not in self.user_db:
            self.username = username
            self.bac_history = []
            self.bac_history_datetimes = []
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
            'latest_bac': self.latest_bac,
            'last_update': self.last_update,
            'points': self.points,
            'user_secret': self.user_secret,
        }

    def load_from_serialized(self, serialized_dict):
        for key in serialized_dict:
            setattr(self, key, serialized_dict[key])

    def update_bac(self, new_bac):
        now = datetime.now()
        self.bac_history.append(float(new_bac))
        self.bac_history_datetimes.append(now)
        self.latest_bac = str(new_bac)
        self.last_update = now.strftime(datetime_string_format)
        self.points += submit_new_bac_points

        self.user_db['user'] = self.serialize()

    def get_user_graph(self):
        if len(self.bac_history) > 0:
            fig = px.line(x=self.bac_history_datetimes, y=self.bac_history, markers=True)
            fig.update_layout(margin=dict(l=0, r=0, b=0, t=0,), xaxis=dict(title="Datetime"), yaxis=dict(title="BAC"))
            return fig
        else:
            layout = go.Layout(margin=go.layout.Margin(l=0, r=0, b=0, t=0), xaxis=dict(title="Datetime"), yaxis=dict(title="BAC"))
            fig = dict(layout=layout)
            return fig