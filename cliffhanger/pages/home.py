from dash import html
import dash_bootstrap_components as dbc
from cliffhanger.pages.page import Page

def layout_function(**kwargs):
    layout = html.Div([
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

callbacks = []

page = Page('/', 'Home', layout_function, callbacks, False)
