from dash import html
import dash_bootstrap_components as dbc
from cliffhanger.pages.page import Page

def layout_function(**kwargs):
    layout = html.Div([
        dbc.Row(
            dbc.Col([
                dbc.Row(
                    html.H3('Welcome home!', style={"text-align": "center", "padding-top": "15px"}),
                    justify="center"
                ),
                dbc.Row(
                    dbc.Button("Join Session", color="primary", className="me-1", style={"margin-top": "15px", "margin-bottom": "15px"}, href="/joinsession"),
                    justify="center"
                ),
                dbc.Row(
                    dbc.Button("New Session", color="secondary", outline=True, className="me-1", style={"margin-top": "15px", "margin-bottom": "15px"}, href="/newsession"),
                    justify="center"
                )], width=3, align="center"
            ), justify="center"
        )
    ])
    return layout

callbacks = []

page = Page('/', 'Home', layout_function, callbacks, True)
