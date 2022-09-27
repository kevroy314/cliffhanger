"""The home page for the application which shows rules and allows basic feature navigation."""
import dash_bootstrap_components as dbc
from dash import html
from dash.dependencies import Input, Output

from cliffhanger.pages.page import Page


def layout_function(**kwargs):  # pylint: disable=unused-argument
    """Return a layout object for the home page."""
    layout = html.Div([
        html.Div([
            dbc.Modal([
                dbc.ModalHeader(dbc.ModalTitle("Rules")),
                dbc.ModalBody(
                    html.Ul([
                        html.Li([html.Span("Rule 1: ", className="rule-item"), "Keep it fun!"]),
                        html.Li([html.Span("Rule 2: ", className="rule-item"), "Enter your BAC once per hour"]),
                        html.Li([html.Span("Rule 3: ", className="rule-item"), "Wait 15min after your last sip of alcohol before blowing (hint: use the timer)"]),
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
