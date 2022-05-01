from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

def cards_user_components(session_id, username):
    # TODO: Get data from database as needed
    n_points = 123
    n_cards = 3
    n_cards_played_on_you = 1

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

    resolve_card_modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Resolve Cards")),
                    dbc.ModalBody("Wow this thing takes up a lot of space..."),
                    dbc.Button("Done", id="resolve-card-btn")
                    # TODO: Add card resolution ui
                ],
                id="resolve-card-modal",
                fullscreen=True,
                is_open=False
            ),
        ]
    )

    return dbc.Row([
        dbc.Col(dbc.Button(["Buy Cards", 
            dbc.Badge(str(n_points), color="light", text_color="primary", className="ms-1")],
        id="buy-card-modal-btn", color="success", className="menu-btn", disabled=n_cards_played_on_you!=0)),
        dbc.Col(dbc.Button(["Play Cards", 
            dbc.Badge(str(n_cards), color="light", text_color="primary", className="ms-1")], 
        id="play-card-modal-btn", color="info", className="menu-btn", disabled=n_cards_played_on_you!=0)),
        html.Div(
            dbc.Col(dbc.Button(["Resolve Cards", 
                dbc.Badge(str(n_cards_played_on_you), color="light", text_color="primary", className="ms-1")], 
            id="resolve-card-modal-btn", color="danger", className="menu-btn")), style={'padding-top': '10px'}
        ),
        play_card_modal,
        buy_card_modal,
        resolve_card_modal
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

def resolve_card(n_clicks_open, n_clicks_place, is_open):
    if n_clicks_open is None:
        return False
    if n_clicks_open > 0 and (not is_open):
        # Open was clicked
        return True
    if n_clicks_place > 0 and is_open:
        print("resolve card")
        # TODO: Add card resolve logic
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
    [[Output("resolve-card-modal", "is_open"),
     [Input("resolve-card-modal-btn", "n_clicks"), Input("resolve-card-btn", "n_clicks")],
     [State("resolve-card-modal", "is_open")]],
     resolve_card],
]