from dash import html
from cliffhanger.pages.page import Page


layout = html.Div([
    html.H3('Welcome newuser!'),
])

callbacks = []

page = Page('/newuser', 'New User', layout, callbacks)
