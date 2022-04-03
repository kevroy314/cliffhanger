from dash import html
from cliffhanger.pages.page import Page


layout = html.Div([
    html.H3('Welcome play!'),
])

callbacks = []

page = Page('/play', 'Play', layout, callbacks)
