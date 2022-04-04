from dash import html
import dash_bootstrap_components as dbc
from cliffhanger.pages.page import Page
from cliffhanger.database.db import new_session

def layout_function(**kwargs):
    session_id = new_session()
    layout = html.Div([
        dbc.Row(
            dbc.Col([
                dbc.Row(
                    html.H3('Session Code', style={"text-align": "center", "padding-top": "15px"}),
                    justify="center"
                ),
                dbc.Row(
                    [html.Sub('Share This With Participants', style={"text-align": "center"}), html.Br(), html.Sub('(not case sensitive)', style={"text-align": "center", "margin-top": "-5px"})],
                    justify="center"
                ),
                dbc.Row(html.H4(session_id, style={"text-align": "center", "margin-top": "25px", "margin-bottom": "25px"}),
                    justify="center"),
                dbc.Row(
                    dbc.Button("Join Session", color="primary", className="me-1", href=f"/joinsession/{session_id}"),
                    justify="center"
                ),
            ], width=3),
            justify="center"
        )
    ])
    return layout

callbacks = []

page = Page('/newsession', 'New Session', layout_function, callbacks, True)
