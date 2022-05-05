"""The home page for the application which shows rules and allows basic feature navigation."""
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from cliffhanger.pages.page import Page


def layout_function(**kwargs):
    """Return a layout object for the home page."""
    layout = html.Div([
        html.Div([
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Rules")),
                dbc.ModalBody(
                    html.Ul([
                        html.Li([html.Span("Rule 1: ", className="rule-item"), "Keep it fun!"]),
                        html.Li([html.Span("Rule 2: ", className="rule-item"), "Enter your BAC once per hour"]),
                        html.Li([html.Span("Rule 3: ", className="rule-item"), "Wait 15min after your last sip of alcohol before blowing (hint: use the timer for bonus points)"]),
                        html.Li([html.Span("Rule 4: ", className="rule-item"), "Use points earned from entering your data to place bets on your BAC, other player BACs, or the party average BAC each hour (hint: it's not about drinking the most, but knowing the most)"]),
                        html.Li([html.Span("Rule 5: ", className="rule-item"), "Spend your points on cards to play on other players to impact their next BAC blow"]),
                        html.Li([html.Span("Rule 6: ", className="rule-item"), "You can only place bets, play cards, and buy cards if you've resolved all the cards played on you."]),
                    ])),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close-rules", className="ms-auto", n_clicks=0)
                )],
                id="rules-modal",
                is_open=True,
            )]),
        dbc.Row(
            dbc.Col([
                dbc.Row(
                    html.H2('Welcome home!', className="page-title"),
                    justify="center", align="center"
                ),
                dbc.Row(
                    dbc.Button("Join Session", color="primary", className="me-1 action-btn", href="/joinsession"),
                    justify="center", align="center"
                ),
                dbc.Row(
                    dbc.Button("New Session", color="secondary", outline=True, className="me-1 action-btn", href="/newsession"),
                    justify="center", align="center"
                )], width=10, align="center"
            ), justify="center", align="center", style={"height": "80vh"}
        )
    ])
    return layout


def close_rules(n_clicks):
    """Close the rules modal on click."""
    if n_clicks == 0:
        return True
    else:
        return False


callbacks = [[[Output("rules-modal", "is_open"), Input("close-rules", "n_clicks")], close_rules]]

page = Page('/', 'Home', layout_function, callbacks, False)
