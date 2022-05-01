from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from flask import session


def bets_user_current_bets(session_id, username):
    table_header = [
        html.Thead(html.Tr([
            html.Th("User", className="party-table-header-item"), 
            html.Th("Last BAC", className="party-table-header-item"), 
            html.Th("Bet BAC", className="party-table-header-item"), 
            html.Th("Wager", className="party-table-header-item"),
            html.Th("Result", className="party-table-header-item"),
        ]))
    ]

    rows = []
    bets = []
    if len(bets) == 0:
        rows = [html.Tr([
                   html.Td("No Bets"),
                   html.Td("No Bets"),
                   html.Td("No Bets"),
                   html.Td("No Bets"),
                   html.Td("No Bets")
               ])]
    # rows = []
    # for username in session.users:
    #     user = session.users[username]
    #     row = html.Tr([
    #         html.Td(user.username),
    #         html.Td(user.latest_bac),
    #         html.Td(user.last_update),
    #         html.Td(str(user.points))
    #     ])
    #     rows.append(row)
    
    table_body = [html.Tbody(rows)]
    table = dbc.Table(table_header + table_body, bordered=True, className="party-table")
    return table

def bets_party_current_bets(session_id):
    table_header = [
        html.Thead(html.Tr([
            html.Th("User", className="party-table-header-item"), 
            html.Th("Last BAC", className="party-table-header-item"), 
            html.Th("Bet BAC", className="party-table-header-item"), 
            html.Th("Wager", className="party-table-header-item")
        ]))
    ]

    rows = []
    bets = []
    if len(bets) == 0:
        rows = [html.Tr([
                   html.Td("No Bets"),
                   html.Td("No Bets"),
                   html.Td("No Bets"),
                   html.Td("No Bets")
               ])]
    # rows = []
    # for username in session.users:
    #     user = session.users[username]
    #     row = html.Tr([
    #         html.Td(user.username),
    #         html.Td(user.latest_bac),
    #         html.Td(user.last_update),
    #         html.Td(str(user.points))
    #     ])
    #     rows.append(row)
    
    table_body = [html.Tbody(rows)]
    table = dbc.Row([html.H4("Party Active Bets"), dbc.Table(table_header + table_body, bordered=True, className="party-table")])
    return table

def bets_user_components(session_id, username):
    # TODO: Get data from database as needed
    n_cards_played_on_you = 0

    player_bet_modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Place Player Bet")),
                    dbc.ModalBody("Wow this thing takes up a lot of space..."),
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
                    dbc.ModalBody("Wow this thing takes up a lot of space..."),
                    dbc.Button("Place Bet", id="party-bet-place-btn")
                ],
                id="party-bet-modal",
                fullscreen=True,
                is_open=False
            ),
        ]
    )
    return dbc.Row([
        dbc.Col(dbc.Button("Player Bet", id="player-bet-btn", className="menu-btn", color="warning", disabled=n_cards_played_on_you!=0)),
        dbc.Col(dbc.Button("Party Bet", id="party-bet-btn", className="menu-btn", color="warning", disabled=n_cards_played_on_you!=0)),
        dbc.Row(bets_user_current_bets(session_id, username)),
        player_bet_modal,
        party_bet_modal
    ], style={"padding-bottom": "5px"})

def bets_session_components(session_id):
    return bets_party_current_bets(session_id)

def player_bet(n_clicks_open, n_clicks_place, is_open):
    if n_clicks_open is None:
        return False
    if n_clicks_open > 0 and (not is_open):
        # Open was clicked
        return True
    if n_clicks_place > 0 and is_open:
        print("place player bet")
        # Place bet was clicked
        return False

def party_bet(n_clicks_open, n_clicks_place, is_open):
    if n_clicks_open is None:
        return False
    if n_clicks_open > 0 and (not is_open):
        # Open was clicked
        return True
    if n_clicks_place > 0 and is_open:
        print("place party bet")
        # Place bet was clicked
        return False

bets_callbacks = [
    [[Output("player-bet-modal", "is_open"),
     [Input("player-bet-btn", "n_clicks"), Input("player-bet-place-btn", "n_clicks")],
     [State("player-bet-modal", "is_open")]],
     player_bet],
    [[Output("party-bet-modal", "is_open"),
     [Input("party-bet-btn", "n_clicks"), Input("party-bet-place-btn", "n_clicks")],
     [State("party-bet-modal", "is_open")]],
     party_bet],
]