"""The cards features are in this module."""
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output, State


def cards_user_components(session_id, username):
    """Get the user components for the cards feature.

    Args:
        session_id (str): the session id
        username (str): the username

    Returns:
        dbc.Row: a Row object containing the cards user features
    """
    # TODO: Get data from database as needed
    n_points = 123
    n_cards = 3
    n_cards_played_on_you = 0

    store = dbc.Carousel(
        items=[
            {
                "key": "1",
                "src": "/assets/images/level-1.png",
                "header": "Level 1 Cards",
                "caption": "Cost: 100 points",
            },
            {
                "key": "2",
                "src": "/assets/images/level-2.png",
                "header": "Level 2 Cards",
                "caption": "Cost: 200 points",
            },
            {
                "key": "3",
                "src": "/assets/images/level-3.png",
                "header": "Level 3 Cards",
                "caption": "Cost: 300 points",
            },
        ]
    )

    inventory = dbc.Carousel(
        items=[
            {
                "key": "1",
                "src": "/assets/images/output.png",
            },
        ]
    )

    resolve_inventory = dbc.Carousel(
        items=[
            {
                "key": "1",
                "src": "/assets/images/output.png",
            },
        ]
    )

    buy_card_modal = html.Div(
        [
            dbc.Modal(
                [
                    dbc.ModalHeader(dbc.ModalTitle("Select Card")),
                    dbc.ModalBody(store),
                    dbc.Button("Buy Card", id="buy-card-btn")
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
                    dbc.ModalBody(inventory),
                    dbc.Button("Play Card", id="play-card-btn")
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
                    dbc.ModalBody(resolve_inventory),
                    dbc.Button("Done", id="resolve-card-btn")
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
            id="buy-card-modal-btn", color="success", className="menu-btn", disabled=n_cards_played_on_you != 0)),
        dbc.Col(dbc.Button(["Play Cards",
                dbc.Badge(str(n_cards), color="light", text_color="primary", className="ms-1")],
            id="play-card-modal-btn", color="info", className="menu-btn", disabled=n_cards_played_on_you != 0)),
        html.Div(dbc.Col(dbc.Button(["Resolve Cards",
                                     dbc.Badge(str(n_cards_played_on_you), color="light", text_color="primary", className="ms-1")],
                         id="resolve-card-modal-btn", color="danger", className="menu-btn")), style={'padding-top': '10px'}),
        play_card_modal,
        buy_card_modal,
        resolve_card_modal
    ])


def play_card(n_clicks_open, n_clicks_place, is_open):
    """Perform the logic needed for when a card is played."""
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
    """Perform the logic needed for when a card is purchased."""
    if n_clicks_open is None:
        return False
    if n_clicks_open > 0 and (not is_open):
        # Open was clicked
        return True
    if n_clicks_place > 0 and is_open:
        print("buy card")
        # TODO: Add card buy logic
        # TODO: Use carflip.html visualization to reveal card when bought
        return False


def resolve_card(n_clicks_open, n_clicks_place, is_open):
    """Perform the logic needed for when a card is resolved."""
    if n_clicks_open is None:
        return False
    if n_clicks_open > 0 and (not is_open):
        # Open was clicked
        return True
    if n_clicks_place > 0 and is_open:
        print("resolve card")
        # TODO: Add card resolve logic
        # TODO: Use carflip.html visualization to reveal card when opened

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
