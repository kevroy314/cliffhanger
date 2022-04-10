import logging
from datetime import datetime
from inspect import trace
import traceback

import pandas as pd

from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from cliffhanger.pages.page import Page
from cliffhanger.database.session import Session
from cliffhanger.database.user import User
from cliffhanger.utils.formats import datetime_string_format

def generate_user_table(session):
    table_header = [
        html.Thead(html.Tr([
            html.Th("User", className="party-table-header-item"), 
            html.Th("Last BAC", className="party-table-header-item"), 
            html.Th("Last Updated", className="party-table-header-item"), 
            html.Th("Points", className="party-table-header-item")
        ]))
    ]

    rows = []
    for username in session.users:
        user = session.users[username]
        row = html.Tr([
            html.Td(user.username),
            html.Td(user.latest_bac),
            html.Td(user.last_update),
            html.Td(str(user.points))
        ])
        rows.append(row)

    table_body = [html.Tbody(rows)]
    table = dbc.Table(table_header + table_body, bordered=True, className="party-table")
    return table

def session_page(**kwargs):
    session_id = kwargs['path_meta'][0]
    session = Session.get_session(session_id)
    most_recent_user = kwargs['user-preferences-data']['most_recent_user']
    layout = html.Div([
            dbc.Row(
                dbc.Col([
                    dbc.Row(
                        html.H2(f'Welcome to the {session_id} party!', className="page-title"),
                        justify="center"
                    ),
                    dbc.Row(
                        html.H4(f'Invite more people!', className="page-title"),
                        justify="center"
                    ),
                    dbc.Row(html.Img(src=f"/assets/qrcodes/{session_id}.png", className="session-id-qr"), 
                        justify="center"),
                    dbc.Button(html.I(className="fa fa-solid fa-download"), id="download-session-snapshop-btn", className="data-download-button", color="secondary", outline=True),
                    dcc.Download(id="download-controller"),
                    generate_user_table(session),
                    dcc.Graph(figure=session.create_session_graph()),
                    dcc.Graph(figure=session.create_session_score_graph()),
                    dbc.Row(
                        dbc.Button("Go to My User Page", color="primary", className="me-1 action-btn", href=f"/play/{session_id}/{most_recent_user}"), # TODO - make this link right
                        justify="center"
                    ),
                ], width=10),
                justify="center"
            )
        ])
    return layout

def user_page(**kwargs):
    session_id, username = kwargs['path_meta']
    data = kwargs['user-preferences-data']
    user = User(session_id, username)
    secret_key = session_id+"_"+username+"_secret"
    if secret_key not in data:
        logging.warn("No secret key, disallowing user page loading")
        return error_page(**kwargs) # Unauthorized
    if data[secret_key] != user.user_secret:
        logging.warn("Wrong secret key, disallowing user page loading")
        return error_page(**kwargs) # Unauthorized

    layout = html.Div([
        html.Script(src="/assets/components/countdown/countdown.js"),
        dbc.Row(
            dbc.Col([
                dbc.Row(
                    html.H3(f'Welcome {username}!', className="page-title"),
                    justify="center"
                ),
                dbc.Row(
                    [html.Sub(f'You are in session {session_id}.', className="subtitle"), html.Br()],
                    justify="center"
                ),
                dbc.Row(
                    [html.Sub(f'You currently have {user.points} points.', className="subtitle", id="points-display"), html.Br()],
                    justify="center"
                ),
                dbc.Row(
                    html.Div(id="countdown-timer", className="countdown-timer"),
                    justify="center"
                ),
                dbc.Row(
                    dbc.Input(value="0.000", className="me-1 bac-input-text", id="input-bac", type="number", min=0, max=1, step=0.001),
                    justify="center"
                ),
                dbc.Row([
                    dbc.Label("What did you drink?"),
                    dbc.Checklist(
                        options=[
                            {"label": "Nothing", "value": 1},
                            {"label": "Beer", "value": 2},
                            {"label": "Wine", "value": 3},
                            {"label": "Liquor (Drinks)", "value": 4},
                            {"label": "Liquor (Shots)", "value": 5},
                        ],
                        value=[],
                        id="drink-description-checklist",
                        inline=True,
                    )],
                    justify="center"
                ),
                dbc.Row(
                    dbc.Button("Submit BAC", color="primary", className="me-1 action-btn", id="submit-bac"),
                    justify="center"
                ),
                dbc.Row(
                    dbc.Button("Go to Party Page", color="secondary", outline=True, className="me-1 action-btn", href=f"/play/{session_id}"),
                    justify="center"
                ),
                dbc.Row(
                    html.P("", className="confirmation-text", id="confirmation-text"),
                    justify="center"
                ),
                dcc.Graph(id="user-graph"),
                dbc.Row([
                        dbc.Input(value=username, id="play-username"),
                        dbc.Input(value=session_id, id="play-session-id")
                    ],
                    className="hide"
                    
                ),
            ], width=10),
            justify="center"
        )
    ])
    return layout

def error_page(**kwargs):
    layout = html.Div([
        dbc.Row(
            dbc.Col([
                dbc.Row(
                    html.H3('There was an error, how did you get here? Go Home!', className="error-text"),
                    justify="center"
                ),
                dbc.Row(
                    dbc.Button("Go Home", color="primary", className="me-1", href="/"),
                    justify="center"
                ),
            ], width=10),
            justify="center"
        )
    ])
    return layout

def layout_function(**kwargs):
    try:
        if len(kwargs['path_meta']) == 1:
            return session_page(**kwargs)
        elif len(kwargs['path_meta']) == 2:
            return user_page(**kwargs)
        else:
            logging.warn("Bad URL format, going to play error page")
            return error_page(**kwargs)
    except Exception as e:
        logging.warn("Unexpected error, going to play error page. Printing traceback")
        traceback.print_exc()
        return error_page(**kwargs)


def on_submit_new_bac(n_clicks, bac, username, session_id, data, javascript_data, drink_description_checklist):
    user = User(session_id, username)
    if n_clicks is not None:
        timer_value = None    
        if "timeLeft" in javascript_data:
            timer_value = javascript_data['timeLeft']
        user = User(session_id, username)
        secret_key = session_id+"_"+username+"_secret"
        if secret_key not in data:
            graph = user.get_user_graph()
            return (["You are not authorized to do this."], graph, f'You currently have {user.points} points.')
        if data[secret_key] != user.user_secret:
            graph = user.get_user_graph()
            return (["You are not authorized to do this."], graph, f'You currently have {user.points} points.')
        now = datetime.now()
        user.update_bac(bac, timer_value, drink_description_checklist)
        graph = user.get_user_graph()
        return (["Submitted Successfully!", html.Br(), f"({now.strftime(datetime_string_format)})"], graph, f'You currently have {user.points} points.')
    else:
        graph = user.get_user_graph()
        return ("", graph, f'You currently have {user.points} points.')

def download_session_snapshop(n_clicks, data):
    if n_clicks is not None:
        session_id = data['most_recent_session']
        datestr = datetime.now().strftime(datetime_string_format.replace('/', "-").replace(":", "-").replace(" ", "_"))
        df = Session(session_id).extract_data_snapshot()
        return dcc.send_data_frame(df.to_csv, f"{session_id}_{datestr}.csv")
    else:
        raise PreventUpdate()

callbacks = [
    [[[Output("confirmation-text", "children"), Output("user-graph", "figure"), Output("points-display", "children")], Input("submit-bac", "n_clicks"), [State("input-bac", "value"), State("play-username", "value"), State("play-session-id", "value"), State("user-preferences", "data"), State("javascript-variables", "data"), State("drink-description-checklist", "value")]], on_submit_new_bac],
    [[Output("download-controller", "data"), [Input("download-session-snapshop-btn", "n_clicks")], [State("user-preferences", "data")]], download_session_snapshop],
]

page = Page('/play', 'Play', layout_function, callbacks, False)
