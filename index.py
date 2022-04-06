from cliffhanger.utils.log import initialize_logging
import os
initialize_logging("logs/app_logs.log")

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from cliffhanger.pages import pages
from cliffhanger.components.navbar import create_navbar


app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=[dbc.themes.LUX, "/assets/css/cliffhanger.css"],
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])
server = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    create_navbar(pages),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    layout_args = {}
    if pathname.count('/') > 1:
        # assume it's a data path
        path_components = [x for x in pathname.split('/') if x]
        pathname = '/'+path_components[0]
        layout_args['path_meta'] = path_components[1:]
    for page in pages:
        if page is not None:
            if pathname == page.url:
                return page.layout_function(**layout_args)
    return pages[0].layout

for page in pages:
    if page is None:
        continue
    for callback in page.callbacks:
        ios_definitions, function_definition = callback
        app.callback(*ios_definitions)(function_definition)

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)