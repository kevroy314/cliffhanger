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
    return dbc.Row([
        dbc.Col(dbc.Button("Player Bet", id="player-bet-btn", className="menu-btn")),
        dbc.Col(dbc.Button("Party Bet", id="party-bet-btn", className="menu-btn")),
        dbc.Row(bets_user_current_bets(session_id, username))
    ], style={"padding-bottom": "5px"})

def bets_session_components(session_id):
    return bets_party_current_bets(session_id)

bets_callbacks = []