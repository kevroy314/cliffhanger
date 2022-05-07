"""The main entry point of the application."""
import dash_bootstrap_components as dbc
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State

import cliffhanger.utils.log  # pylint: disable=unused-import
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

for _page in pages:
    if _page is None:
        continue
    for callback in _page.callbacks:
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
    """Display a page on callback when the url changes."""
    layout_args = {}
    layout_args['href'] = href
    layout_args['user-preferences-data'] = data
    if pathname.count('/') > 1:
        # assume it's a data path
        path_components = [x for x in pathname.split('/') if x]
        pathname = '/' + path_components[0]
        layout_args['path_meta'] = path_components[1:]
    for page in pages:
        if page is not None:
            if pathname == page.url:
                return page.layout_function(**layout_args)
    return pages[0].layout_function(**layout_args)


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True, port=8050)
