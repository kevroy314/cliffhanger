"""The main play page of the application."""
import logging
import traceback
from datetime import datetime

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

from cliffhanger.database.session import Session
from cliffhanger.database.user import User
from cliffhanger.pages.page import Page
from cliffhanger.utils.formats import DATETIME_STRING_FORMAT

def get_coin_modal():
    return dbc.Modal([
            dbc.ModalHeader(dbc.ModalTitle("Get 100 Coin!")),
            dbc.ModalBody([
                html.Img(src='/assets/images/coin.png'),
            ]),
            dbc.ModalFooter(
                dbc.Button("Got it!", id="close-coin-modal", className="ms-auto", n_clicks=0)
            )],
            id="coin-modal",
            is_open=False,
        )


def generate_user_table(session):
    """Given a session object, generate the table describing the current user states.

    Args:
        session (cliffhanger.database.session.Session): a session object (already initialized)

    Returns:
        dbc.Row: a Row object containing the status table
    """
    table_header = [
        html.Thead(html.Tr([
            html.Th("User", className="party-table-header-item"),
            html.Th("Last BAC", className="party-table-header-item"),
            html.Th("Last Updated", className="party-table-header-item")
        ]))
    ]

    rows = []
    for username in session.users:
        user = session.users[username]
        row = html.Tr([
            html.Td(user.username),
            html.Td(user.latest_bac),
            html.Td(user.last_update)
        ])
        rows.append(row)

    table_body = [html.Tbody(rows)]
    table = dbc.Row([html.H4("Party Status", style={"padding-top": "10px"}), dbc.Table(table_header + table_body, bordered=True, className="party-table")])
    return table


def session_page(**kwargs):
    """Return a layout object representing the overview of the current session."""
    session_id = kwargs['path_meta'][0]
    session = Session.get_session(session_id)
    most_recent_user = kwargs['user-preferences-data']['most_recent_user']
    try:
        prev_party_average_bac = f"{float(session.get_stat('prev_party_average')):.3}"
    except KeyError:
        prev_party_average_bac = "None Yet"
    try:
        party_average_bac = f"{float(session.get_stat('party_average')):.3}"
    except KeyError:
        party_average_bac = "None Yet"
    try:
        prev_bet = f"{float(session.get_stat('prev_party_next_bet')):.3}"
    except KeyError:
        prev_bet = "None Yet"
    try:
        next_bet = f"{float(session.get_stat('party_next_bet')):.3}"
    except KeyError:
        next_bet = "None Yet"
    next_bet_evalution_time_left = 60 - datetime.now().time().minute
    party_average_card = dbc.Card([
            dbc.CardBody([
                    html.H4("Party Avg. BAC", className="card-title center-text"),
                    html.P(f"{party_average_bac}", className="card-text large-number-text center-text", id="party-average-card"),
                ]),
            dbc.CardFooter([f"Next bet in {next_bet_evalution_time_left} minutes.", html.Br(), 
                            f"Last Avg. BAC was {prev_party_average_bac}"], className="center-text")],
        style={"width": "18rem"},
    )
    next_bet_card = dbc.Card([
            dbc.CardBody([
                    html.H4("Next Bet BAC", className="card-title center-text"),
                    html.P(f"{next_bet}", className="card-text large-number-text center-text", id="next-bet-card"),
                ]),
            dbc.CardFooter([f"Next bet in {next_bet_evalution_time_left} minutes.", html.Br(), 
                            f"Last Bet BAC was {prev_bet}"], className="center-text")],
        style={"width": "18rem"},
    )
    layout = html.Div([
        dbc.Row(
            dbc.Col([
                dbc.Row(
                    html.H2(f'Welcome to the {session_id} party!', className="page-title"),
                    justify="center"
                ),
                dbc.Row(
                    html.H4('Invite more people!', className="page-title"),
                    justify="center"
                ),
                dbc.Row([
                    next_bet_card,
                    html.Img(src=f"/assets/qrcodes/{session_id}.png", className="session-id-qr"),
                    party_average_card,
                ], justify="center"),
                dbc.Button(html.I(className="fa fa-solid fa-download"), id="download-session-snapshop-btn", className="data-download-button", color="secondary", outline=True),
                dcc.Download(id="download-controller"),
                generate_user_table(session),
                dcc.Graph(figure=session.create_session_graph()),
                dbc.Row(
                    dbc.Button("Go to My User Page", color="primary", className="me-1 action-btn", href=f"/play/{session_id}/{most_recent_user}"),
                    justify="center"
                ),
                dbc.Row([
                        dbc.Input(value=most_recent_user, id="play-username"),
                        dbc.Input(value=session_id, id="play-session-id")
                        ], className="hide"),
            ], width=10),
            justify="center"
        )
    ])
    return layout


def user_page(**kwargs):
    """Return a layout object representing the current user's actions (note, they must have created this user on this device)."""
    session_id, username = kwargs['path_meta']
    data = kwargs['user-preferences-data']
    user = User(session_id, username, create_if_not_exist=False)
    secret_key = session_id + "_" + username + "_secret"
    if secret_key not in data:
        logging.warning("No secret key, disallowing user page loading")
        return error_page(**kwargs)  # Unauthorized
    if data[secret_key] != user.user_secret:
        logging.warning("Wrong secret key, disallowing user page loading")
        return error_page(**kwargs)  # Unauthorized

    layout = html.Div([
        get_coin_modal(),
        dbc.Row(
            dbc.Col([
                dbc.Row(
                    html.H3(f'Welcome {username}!', className="page-title"),
                    justify="center"
                ),
                dbc.Row(
                    [html.Sub(f'You are in session {session_id}.', className="subtitle")],
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
                        ], className="hide"),
            ], width=10),
            justify="center"
        )
    ])
    return layout


def error_page(**kwargs):  # pylint: disable=unused-argument
    """Show an error if anything goes wrong."""
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
    """Return the appropriate layout given the path following /play/* ."""
    try:
        if len(kwargs['path_meta']) == 1:
            return session_page(**kwargs)
        elif len(kwargs['path_meta']) == 2:
            return user_page(**kwargs)
        else:
            logging.warning("Bad URL format, going to play error page")
            return error_page(**kwargs)
    except Exception:  # pylint: disable=broad-except
        logging.warning("Unexpected error, going to play error page. Printing traceback")
        traceback.print_exc()
        return error_page(**kwargs)


def on_submit_new_bac(n_clicks, n_clicks_close_coin_modal, bac, session_id, username, data, drink_description_checklist):
    """Respond to submissions of new BAC values on callback."""
    user = User(session_id, username, create_if_not_exist=False)
    if callback_context.triggered[0]['prop_id'] == '.':
        graph = user.get_user_graph()
        return ("", graph, False)
    if callback_context.triggered[0]['prop_id'] == 'submit-bac.n_clicks':
        if n_clicks is not None:
            secret_key = session_id + "_" + username + "_secret"
            if secret_key not in data:
                graph = user.get_user_graph()
                return (["You are not authorized to do this."], graph, False)
            if data[secret_key] != user.user_secret:
                graph = user.get_user_graph()
                return (["You are not authorized to do this."], graph, False)
            now = datetime.now()
            get_coins, time_left_in_minutes_to_next_coin = user.update_bac(bac, drink_description_checklist)
            graph = user.get_user_graph()
            if get_coins:
                return (["Submitted Successfully!", html.Br(), f"({now.strftime(DATETIME_STRING_FORMAT)})"], graph, True)
            else:
                return (["Submitted Successfully!", html.Br(), f"You submitted early. Submit again in {time_left_in_minutes_to_next_coin:.2f} minutes to get more coins.", html.Br(), f"({now.strftime(DATETIME_STRING_FORMAT)})"], graph, False)
        else:
            graph = user.get_user_graph()
            return ("", graph, False)
    elif callback_context.triggered[0]['prop_id'] == 'close-coin-modal.n_clicks':
        graph = user.get_user_graph()
        if n_clicks_close_coin_modal == 0:
            return ("", graph, True)
        else:
            return ("", graph, False)


def download_session_snapshot(n_clicks, data):
    """Begin a download of the current session data when requested."""
    if n_clicks is not None:
        session_id = data['most_recent_session']
        datestr = datetime.now().strftime(DATETIME_STRING_FORMAT.replace('/', "-").replace(":", "-").replace(" ", "_"))
        df = Session(session_id).extract_data_snapshot()
        return dcc.send_data_frame(df.to_csv, f"{session_id}_{datestr}.csv")
    else:
        raise PreventUpdate()

def close_coin_modal(n_clicks):
    """Close the coins modal on click."""
    if n_clicks == 0:
        return True
    else:
        return False


callbacks = [
    [[[Output("confirmation-text", "children"), Output("user-graph", "figure"), Output("coin-modal", "is_open")], [Input("submit-bac", "n_clicks"), Input("close-coin-modal", "n_clicks")], [State("input-bac", "value"), State("play-session-id", "value"), State("play-username", "value"), State("user-preferences", "data"), State("drink-description-checklist", "value")]], on_submit_new_bac],
    [[Output("download-controller", "data"), [Input("download-session-snapshop-btn", "n_clicks")], [State("user-preferences", "data")]], download_session_snapshot],
]

page = Page('/play', 'Play', layout_function, callbacks, False)
