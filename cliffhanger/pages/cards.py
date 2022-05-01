from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

def cards_user_components(session_id, username):
    n_points = 123
    n_cards = 3

    buy_card_modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Buy a Card")),
                    dbc.ModalBody("Wow this thing takes up a lot of space..."),
                    dbc.Button("Buy Card", id="buy-card-btn")
                    # TODO: Add store
                ],
                id="buy-card-modal",
                fullscreen=True,
                is_open=False
            ),
        ]
    )
    play_card_modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Play a Card")),
                    dbc.ModalBody("Wow this thing takes up a lot of space..."),
                    dbc.Button("Play Card", id="play-card-btn")
                    # TODO: Add inventory management
                ],
                id="play-card-modal",
                fullscreen=True,
                is_open=False
            ),
        ]
    )

    return dbc.Row([
        dbc.Col(dbc.Button(["Buy Cards", 
            dbc.Badge(str(n_points), color="light", text_color="primary", className="ms-1")],
        id="buy-card-modal-btn", className="menu-btn")),
        dbc.Col(dbc.Button(["Play Cards", 
            dbc.Badge(str(n_cards), color="light", text_color="primary", className="ms-1")], 
        id="play-card-modal-btn", className="menu-btn")),
        play_card_modal,
        buy_card_modal
    ])

def play_card(n_clicks_open, n_clicks_place, is_open):
    if n_clicks_open is None:
        return False
    if n_clicks_open > 0 and (not is_open):
        # Open was clicked
        return True
    if n_clicks_place > 0 and is_open:
        print("play card")
        # TODO: Add card play logic
        return False

def buy_card(n_clicks_open, n_clicks_place, is_open):
    if n_clicks_open is None:
        return False
    if n_clicks_open > 0 and (not is_open):
        # Open was clicked
        return True
    if n_clicks_place > 0 and is_open:
        print("buy card")
        # TODO: Add card buy logic
        return False

cards_callbacks = [
    [[Output("play-card-modal", "is_open"),
     [Input("play-card-modal-btn", "n_clicks"), Input("play-card-btn", "n_clicks")],
     [State("play-card-modal", "is_open")]],
     play_card],
    [[Output("buy-card-modal", "is_open"),
     [Input("buy-card-modal-btn", "n_clicks"), Input("buy-card-btn", "n_clicks")],
     [State("buy-card-modal", "is_open")]],
     buy_card],
]