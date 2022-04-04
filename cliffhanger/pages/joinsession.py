from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from cliffhanger.pages.page import Page
from coolname import generate_slug

def layout_function(**kwargs):
    session_id = ""
    if 'path_meta' in kwargs and len(kwargs['path_meta'])>=1:
        session_id = kwargs['path_meta'][0].lower()
    layout = html.Div([
        dbc.Row(
            dbc.Col([
                dbc.Row(
                    html.H4('Enter Your Username', style={"text-align": "center", "padding-top": "15px"}),
                    justify="center"
                ),
                dbc.Row(dbc.Input(value=generate_slug(2), style={"text-align": "center", "margin-top": "25px", "margin-bottom": "25px"}, id="username"),
                    justify="center"),
                dbc.Row(
                    html.H4('Session ID', style={"text-align": "center", "padding-top": "15px"}),
                    justify="center"
                ),
                dbc.Row(dbc.Input(value=session_id, style={"text-align": "center", "margin-top": "25px", "margin-bottom": "25px"}, id="session-id"),
                    justify="center"),
                dbc.Row(
                    dbc.Button("Join Session", color="primary", className="me-1", id="join-btn"),
                    justify="center"
                ),
            ], width=3),
            justify="center"
        )
    ])
    return layout

def on_username_changed(username, session_id):
    return f"/play/{session_id}/{username}"

callbacks = [
    [[Output("join-btn", "href"), [Input("username", "value"), Input("session-id", "value")]], on_username_changed]
]

page = Page('/joinsession', 'Join Session', layout_function, callbacks, True)
