"""This module coordinates the betting features."""
import dash_bootstrap_components as dbc
from dash import html, dcc, ALL
from dash.dependencies import Input, Output, State

from cliffhanger.database.session import Session
from cliffhanger.database.user import User


class Bet():
    """Store the bet data."""

    def __init__(self, bet_value, bet_user, bet_target):
        """Create a Bet object.

        Args:
            bet_value (float): the value in points that is placed on this bet
            bet_user (str): the username upon which this is bet (None means party next hour)
            bet_target (_type_): the BAC target value for the bet
        """
        self.value = bet_value
        self.user = bet_user  # If none, party
        self.target = bet_target
        self.result = "Unresolved"


def bets_user_current_bets(session_id, username):
    """Get a table describing the user's bet history.

    Args:
        session_id (str): the current session id
        username (str): the current user

    Returns:
        dbc.Row: a Row containing the bet history of this user
    """
    table_header = [
        html.Thead(html.Tr([
            html.Th("User", className="party-table-header-item"),
            html.Th("Last BAC", className="party-table-header-item"),
            html.Th("Bet BAC", className="party-table-header-item"),
            html.Th("Wager", className="party-table-header-item"),
            html.Th("Result", className="party-table-header-item"),
        ]))
    ]

    bets = []
    if username is not None:
        bets = User(session_id, username, create_if_not_exist=False).bets
    rows = []
    if len(bets) == 0:
        rows = [html.Tr([
                html.Td("No Bets"),
                html.Td("No Bets"),
                html.Td("No Bets"),
                html.Td("No Bets"),
                html.Td("No Bets")
                ])]
    else:
        rows = []
        for bet in bets:
            if bet.user is None:
                # Get last party average
                username = "party"
                last_bac = "TODO"  # TODO get party BAC per hour for bet resolution
                bet_bac = bet.target
                wager = bet.value
                result = bet.result
            else:
                bet_user = User(session_id, bet.user, create_if_not_exist=False)
                username = bet.user
                last_bac = bet_user.latest_bac
                bet_bac = bet.target
                wager = bet.value
                result = bet.result
            row = html.Tr([
                html.Td(username),
                html.Td(last_bac),
                html.Td(bet_bac),
                html.Td(wager),
                html.Td(str(result))
            ])
            rows.append(row)

    table_body = [html.Tbody(rows)]
    table = dbc.Table(table_header + table_body, bordered=True, className="party-table")
    return table


def _get_unresolved_bets(session_id):
    # Get all unresolved bets
    session = Session(session_id)
    users = list(session.users.keys())
    bets = []
    for uname in users:
        user = User(session_id, uname)
        user_bets = user.bets
        for bet in user_bets:
            if bet.result == "Unresolved":
                bets.append((uname, bet))
    return bets


def bets_party_current_bets(session_id):
    """Get the current bets for the whole party.

    Args:
        session_id (str): the session id

    Returns:
        dbc.Row: a Row containing the current bets for the party
    """
    bets = _get_unresolved_bets(session_id)

    table_header = [
        html.Thead(html.Tr([
            html.Th("Join?", className="party-table-header-item"),
            html.Th("By", className="party-table-header-item"),
            html.Th("On", className="party-table-header-item"),
            html.Th("Last", className="party-table-header-item"),
            html.Th("Bet", className="party-table-header-item"),
            html.Th("Wager", className="party-table-header-item")
        ]))
    ]

    rows = []
    if len(bets) == 0:
        rows = [html.Tr([
                html.Td("No Bets"),
                html.Td("No Bets"),
                html.Td("No Bets"),
                html.Td("No Bets"),
                html.Td("No Bets"),
                html.Td("No Bets")
                ])]

    else:
        for idx, bet in enumerate(bets):
            uname, bet = bet
            bet_user = User(session_id, uname)
            row = html.Tr([
                dbc.Button("Join", id={"type": "bet-join-btn", "index": idx}),
                html.Td(uname),
                html.Td(bet.user if bet.user else "party"),
                html.Td(str(bet_user.latest_bac)),
                html.Td(str(bet.target)),
                html.Td(str(bet.value))
            ])
            rows.append(row)

    table_body = [html.Tbody(rows)]
    table = dbc.Row([html.Div(id="bet-join-btn-out", style={"display": "none"}), html.H4("Party Active Bets"), dbc.Table(table_header + table_body, bordered=True, className="party-table")])
    return table


def bets_user_components(session_id, username):
    """Return the objects associated with betting that should be rendered on the user screen.

    Args:
        session_id (str): the session id
        username (str): the username

    Returns:
        dbc.Row: a Row object which contains all the user betting controls
    """
    session = Session.get_session(session_id)
    other_users = list(set(list(session.users.keys())) - set([username]))
    user = User(session_id, username, create_if_not_exist=False)

    # TODO: Get data from database as needed
    n_cards_played_on_you = 0

    player_bet_modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Place Player Bet")),
                    dbc.ModalBody([
                        html.H4("Who ya bettin' on?"),
                        dbc.Select(
                            id="player-bet-select",
                            options=[{"label": label, "value": i + 1} for i, label in enumerate(["(me) " + username] + other_users)],
                            value=1
                        ),
                        html.H4("What ya bettin' they'll be next time?"),
                        dbc.Input(id="player-bet-target", value=0.000, type="number", min=0.000, max=1.000, step=0.001),
                        html.H4("How much ya bettin'?"),
                        dbc.Input(id="player-bet-value", value=0, type="number", min=0, max=user.points),
                    ]),
                    dbc.Button("Place Bet", id="player-bet-place-btn")
                ],
                id="player-bet-modal",
                fullscreen=True,
                is_open=False
            ),
        ]
    )
    party_bet_modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Place Party Bet")),
                    dbc.ModalBody([
                        html.H4("What ya bettin' we'll be next hour?"),
                        dbc.Input(id="party-bet-target", value=0.000, type="number", min=0.000, max=1.000, step=0.001),
                        html.H4("How much ya bettin'?"),
                        dbc.Input(id="party-bet-value", value=0, type="number", min=0, max=user.points),
                    ]),
                    dbc.Button("Place Bet", id="party-bet-place-btn")
                ],
                id="party-bet-modal",
                fullscreen=True,
                is_open=False
            ),
        ]
    )
    return dbc.Row([
        dbc.Col(dbc.Button("Player Bet", id="player-bet-btn", className="menu-btn", color="warning", disabled=n_cards_played_on_you != 0)),
        dbc.Col(dbc.Button("Party Bet", id="party-bet-btn", className="menu-btn", color="warning", disabled=n_cards_played_on_you != 0)),
        dbc.Row(id="bets-user-current-bets", children=bets_user_current_bets(session_id, username)),
        dcc.Interval(id="bet-update-interval", interval=2000),
        player_bet_modal,
        party_bet_modal
    ], style={"padding-bottom": "5px"})


def bets_session_components(session_id):
    """Return the current session's bet components.

    Args:
        session_id (str): the session id

    Returns:
        dbc.Row: a Row containing the session components for the bets features
    """
    return bets_party_current_bets(session_id)


def player_bet(n_clicks_open,
               n_clicks_place,
               is_open,
               player_bet_select,
               player_bet_target,
               player_bet_value,
               player_bet_select_options_list,
               session_id,
               username):
    """Handle the player bet workflow in a player bet modal."""
    if n_clicks_open is None:
        return False
    if n_clicks_open > 0 and (not is_open):
        # Open was clicked
        return True
    if n_clicks_place > 0 and is_open:
        selected_user = player_bet_select_options_list[int(player_bet_select) - 1]['label']
        if int(player_bet_select) == 1:
            selected_user = selected_user[5:]
        User(session_id, username, create_if_not_exist=False).add_bet(Bet(player_bet_value, selected_user, player_bet_target))
        # Place bet was clicked
        return False


def party_bet(n_clicks_open,
              n_clicks_place,
              is_open,
              party_bet_target,
              party_bet_value,
              session_id,
              username):
    """Handle the party bet workflow in a party bet modal."""
    if n_clicks_open is None:
        return False
    if n_clicks_open > 0 and (not is_open):
        # Open was clicked
        return True
    if n_clicks_place > 0 and is_open:
        User(session_id, username, create_if_not_exist=False).add_bet(Bet(party_bet_value, None, party_bet_target))
        # Place bet was clicked
        return False


def update_user_bets_interval(n_intervals, session_id, username):
    """Update the current user's bet table and resolves bets appropriately.

    Args:
        n_intervals (int): the number of intervals since page load
        session_id (str): the session id
        username (str): the username

    Returns:
        dbc.Row: a row containing the new user bet table
    """
    # TODO: Add player bet resolution logic
    if n_intervals is not None:
        return bets_user_current_bets(session_id, username)


def join_bet_btn(n_clicks_states, session_id):
    bets = _get_unresolved_bets(session_id)
    print(n_clicks_states)
    print(bets)
    return ""


bets_callbacks = [
    [[Output("bet-join-btn-out", "children"),
      Input({"type": "bet-join-btn", "index": ALL}, 'n_clicks'),
      [State("play-session-id", "value"), State("play-username", "value")]],
     join_bet_btn],
    [[Output("bets-user-current-bets", "children"),
      Input("bet-update-interval", "n_intervals"),
      [State("play-session-id", "value"), State("play-username", "value")]],
     update_user_bets_interval
     ],
    [
        [
            Output("player-bet-modal", "is_open"),
            [
                Input("player-bet-btn", "n_clicks"),
                Input("player-bet-place-btn", "n_clicks")
            ],
            [
                State("player-bet-modal", "is_open"),
                State("player-bet-select", "value"),
                State("player-bet-target", "value"),
                State("player-bet-value", "value"),
                State("player-bet-select", "options"),
                State("play-session-id", "value"), State("play-username", "value")
            ]
        ],
        player_bet
    ],
    [
        [
            Output("party-bet-modal", "is_open"),
            [
                Input("party-bet-btn", "n_clicks"),
                Input("party-bet-place-btn", "n_clicks")
            ],
            [
                State("party-bet-modal", "is_open"),
                State("party-bet-target", "value"),
                State("party-bet-value", "value"),
                State("play-session-id", "value"), State("play-username", "value")
            ]
        ],
        party_bet
    ],
]
