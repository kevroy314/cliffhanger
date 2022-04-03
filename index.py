import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from cliffhanger.pages import pages
from cliffhanger.navbar import create_navbar

app = dash.Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=[dbc.themes.LUX])
server = app.server
app.config.suppress_callback_exceptions = True
print("here")
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    create_navbar(pages),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    print("callback")
    for page in pages:
        if pathname == page.url:
            return page.layout
    return pages[0].layout


if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True)