from dash import html
from cliffhanger.pages.page import Page


layout = html.Div([
    html.H3('Welcome newsession!'),
])

callbacks = []

page = Page('/newsession', 'New Session', layout, callbacks)
