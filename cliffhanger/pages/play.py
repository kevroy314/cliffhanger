from datetime import datetime

from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from cliffhanger.pages.page import Page
from cliffhanger.database.db import get_session, update_session_contents
from cliffhanger.utils.formats import datetime_string_format

def generate_user_table(session):
    table_header = [
        html.Thead(html.Tr([
            html.Th("User", className="party-table-header-item"), 
            html.Th("Latest BAC", className="party-table-header-item"), 
            html.Th("Last Updated", className="party-table-header-item"), 
            html.Th("Points", className="party-table-header-item")
        ]))
    ]

    rows = []
    for username in session.users:
        user = session.users[username]
        history = str(user.bac_history).replace('[', '').replace(']', '')
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
    session = get_session(session_id)

    layout = html.Div([
            dbc.Row(
                dbc.Col([
                    dbc.Row(
                        html.H2(f'Welcome to the {session_id} party!', className="page-title"),
                        justify="center"
                    ),
                    generate_user_table(session),
                    dbc.Row(
                        dbc.Button("Go to My User Page", color="primary", className="me-1 action-btn", href="/"), # TODO - make this link right
                        justify="center"
                    ),
                ], width=10),
                justify="center"
            )
        ])
    return layout

def user_page(**kwargs):
    session_id, username = kwargs['path_meta']
    session = get_session(session_id)
    back = ""
    try:
        session.new_user(username)
        update_session_contents(session)
    except ValueError:
        back = " back"
    layout = html.Div([
        dbc.Row(
            dbc.Col([
                dbc.Row(
                    html.H3(f'Welcome{back} {username}!', className="page-title"),
                    justify="center"
                ),
                dbc.Row(
                    [html.Sub(f'You are in session {session_id}.', className="subtitle"), html.Br()],
                    justify="center"
                ),
                dbc.Row(
                    dbc.Input(value="0.000", className="me-1", id="input-bac", type="number", min=0, max=1, step=0.001),
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
            return error_page(**kwargs)
    except Exception as e:
        print(e)
        return error_page(**kwargs)


def on_submit_new_bac(n_clicks, bac, username, session_id):
    session = get_session(session_id)
    if n_clicks is not None:
        session.users[username].update_bac(bac)
        graph = session.users[username].get_user_graph()
        update_session_contents(session)
        now = datetime.now()
        return (["Submitted Successfully!", html.Br(), f"({now.strftime(datetime_string_format)})"], graph)
    else:
        graph = session.users[username].get_user_graph()
        return ("", graph)

callbacks = [
    [[[Output("confirmation-text", "children"), Output("user-graph", "figure")], Input("submit-bac", "n_clicks"), [State("input-bac", "value"), State("play-username", "value"), State("play-session-id", "value")]], on_submit_new_bac]
]

page = Page('/play', 'Play', layout_function, callbacks, False)
