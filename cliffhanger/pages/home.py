from dash import html
from cliffhanger.pages.page import Page


layout = html.Div([
    html.H3('Welcome home!'),
])

callbacks = []

page = Page('/', 'Home', layout, callbacks)
