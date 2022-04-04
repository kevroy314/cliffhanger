from datetime import datetime
from cliffhanger.point_rules import submit_new_bac_points
import plotly.express as px

class User():
    def __init__(self, username):
        self.username = username
        self.bac_history = []
        self.bac_history_datetimes = []
        self.latest_bac = "Undefined"
        self.last_update = datetime.now().strftime('%m/%d/%Y, %-I:%M%p')
        self.points = 0

    def update_bac(self, new_bac):
        now = datetime.now()
        self.bac_history.append(float(new_bac))
        self.bac_history_datetimes.append(now)
        self.latest_bac = str(new_bac)
        self.last_update = now.strftime('%m/%d/%Y, %-I:%M%p')
        self.points += submit_new_bac_points

    def get_user_graph(self):
        if len(self.bac_history) > 0:
            return px.line(x=self.bac_history_datetimes, y=self.bac_history, markers=True)
        else:
            return {}