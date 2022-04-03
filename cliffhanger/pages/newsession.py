from dash import html
from cliffhanger.pages.page import Page
from cliffhanger.navbar import create_navbar


layout = html.Div([
    html.H3('Welcome newsession!'),
])

callbacks = []

page = Page('newsession', 'New Session', layout, callbacks)
