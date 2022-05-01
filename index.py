from cliffhanger.utils.globals import data_location, log_location
import os
if not os.path.exists(data_location):
    os.mkdir(data_location)
if not os.path.exists(log_location):
    os.mkdir(log_location)
if not os.path.exists("./assets/qrcodes"):
    os.mkdir("./assets/qrcodes")

from cliffhanger.utils.log import initialize_logging

initialize_logging("logs/app_logs.log")

import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from cliffhanger.pages import pages
from cliffhanger.components.navbar import create_navbar

app = dash.Dash(__name__,
                suppress_callback_exceptions=True,
                external_stylesheets=[
                    dbc.themes.LUX,
                    "/assets/css/cliffhanger.css",
                    "/assets/components/countdown/countdown.css",
                    "https://use.fontawesome.com/releases/v6.1.1/css/all.css"
                ],
                meta_tags=[
                    {"name": "viewport", "content": "width=device-width, initial-scale=1"}
                ])
server = app.server

app.layout = html.Div([
    dcc.Interval(id="javascript-variable-crawler", interval=250),
    dcc.Store(id='javascript-variables', storage_type='memory'),
    dcc.Store(id='user-preferences', storage_type='local'),
    dcc.Location(id='url', refresh=False),
    create_navbar(pages),
    html.Div(id='page-content')
])

for page in pages:
    if page is None:
        continue
    for callback in page.callbacks:
        ios_definitions, function_definition = callback
        app.callback(*ios_definitions)(function_definition)

# get javascript variables and store app-wide
app.clientside_callback(
    """
    function(){
        if (typeof variable !== 'undefined')
            return {'timeLeft': timeLeft};
        else
            return {'timeLeft': 900};
    }
    """,
    Output('javascript-variables', 'data'),
    [Input('javascript-variable-crawler', 'n_intervals')],
)

@app.callback(Output('page-content', 'children'), 
              [Input('url', 'pathname')], [State("user-preferences", "data"), State("url", "href")])
def display_page(pathname, data, href):
    layout_args = {}
    layout_args['href'] = href
    layout_args['user-preferences-data'] = data
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

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)