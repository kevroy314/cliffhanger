from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

def cards_user_components(session_id, username):
    n_points = 123
    n_cards = 3
    return dbc.Row([
        dbc.Col(dbc.Button(["Buy Cards", 
        dbc.Badge(str(n_points), color="light", text_color="primary", className="ms-1")], id="buy-cards-btn", className="menu-btn")),
        dbc.Col(dbc.Button(["Play Cards", 
        dbc.Badge(str(n_cards), color="light", text_color="primary", className="ms-1")], id="play-cards-btn", className="menu-btn"))
    ])

cards_callbacks = []