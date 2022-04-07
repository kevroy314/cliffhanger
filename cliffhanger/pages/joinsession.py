from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from cliffhanger.pages.page import Page
from coolname import generate_slug
from cliffhanger.database.session import Session
from dash.exceptions import PreventUpdate

def layout_function(**kwargs):
    session_id = ""
    if 'path_meta' in kwargs and len(kwargs['path_meta'])>=1:
        session_id = kwargs['path_meta'][0].lower()
    layout = html.Div([
        dbc.Row(
            dbc.Col([
                dbc.Row(
                    html.H2('Join Session', className="page-title"),
                    justify="center"
                ),
                dbc.Row(
                    html.H4('Enter Your Username', className="page-title"),
                    justify="center"
                ),
                dbc.Row(dbc.Input(value=generate_slug(2), className="text-input", id="username"),
                    justify="center"),
                dbc.Row(
                    html.H4('Session ID', className="label-title"),
                    justify="center"
                ),
                dbc.Row(dbc.Input(value=session_id, className="text-input", id="session-id"),
                    justify="center"),
                dbc.Row(
                    dbc.Button("Join Session", color="primary", className="me-1 action-btn", id="join-btn"),
                    justify="center"
                ),
            ], width=10),
            justify="center"
        ),
        html.Div(id="hidden_div_for_redirect_callback", className="hide")
    ])
    return layout

def on_username_changed(username, session_id):
    return f"/play/{session_id}/{username}"

def save_username_and_session_on_join(n_clicks, session_id, username, data, href):
    if n_clicks is not None:
        if data is None:
            data = {}
        data['most_recent_session'] = session_id
        if 'session_history' in data:
            data['session_history'] = list(set(list(data['session_history']) + list([session_id])))
        else:
            data['session_history'] = list([session_id])
        if 'usernames' in data:
            data['usernames'] = list(set(list(data['usernames']) + list([session_id+"_"+username])))
        else:
            data['usernames'] = list([session_id+"_"+username])
        session = Session.get_session(session_id)
        data['most_recent_user'] = username
        try:
            user = session.new_user(username)
            data[session_id+"_"+username+"_secret"] = user.user_secret
        except ValueError:
            pass # User already exists - attempt to redirect to user page

        return data, dcc.Location(id="dummy", href=href)
    return data, ""

callbacks = [
    [[Output("join-btn", "href_disabled"), [Input("username", "value"), Input("session-id", "value")]], on_username_changed],
    [[[Output("user-preferences", "data"), Output("hidden_div_for_redirect_callback", "children")], Input("join-btn", "n_clicks"), [State("session-id", "value"), State("username", "value"), State("user-preferences", "data"), State("join-btn", "href_disabled")]], save_username_and_session_on_join]
]

page = Page('/joinsession', 'Join Session', layout_function, callbacks, True)
