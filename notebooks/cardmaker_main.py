import os
import PIL
import json
import plotly.express as px
import dash
from dash.exceptions import PreventUpdate
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import cardmaker

app = dash.Dash(__name__,  external_stylesheets=[dbc.themes.SLATE], assets_folder="./card_maker_assets")

texture_path = 'card_maker_assets/textures'
texture_images, texture_paths = cardmaker.load_images_as_b64("card_maker_assets/textures", include_paths=True)

image_creator = dbc.Modal(
    [
        dbc.ModalHeader(dbc.ModalTitle("Image Creator")),
        dbc.ModalBody([
            dbc.Input(id="image-creator-search-input", placeholder="Search for image..."),
            dbc.Button("Search Google for Images", id="image-creator-search-btn"),
            dcc.Loading(
                id="search-loading",
                type="default",
                fullscreen=True,
                children=html.Div(id="search-loading-output")
            ),
            dbc.Carousel(
                id="image-creator-search-results",
                items=[],
                controls=True,
                indicators=True,
                style={"width": "50vw"}
            ),
            dbc.Select(
                id="image-creator-style-select",
                value="0",
                options=[
                    {"label": "Original Style", "value": "0"},
                    {"label": "Triangulation Style", "value": "1"},
                ],
            ),
            dcc.Graph(id="image-creator-graph"),
            dbc.Button("Crop to View and Save", id="image-creator-save-btn"),
        ]),
    ],
    id="image-creator-modal",
    fullscreen=True,
)

main_layout = html.Div([
    html.H1("Cardmaker"),
    html.Hr(),
    html.H2("Text Elements"),
    dbc.Label("Card Name"),
    dbc.Input(id="card-name", type="text", placeholder="Insert Card Name"),
    dbc.Label("Card Description"),
    dbc.Input(id="card-description", type="text", placeholder="Insert Card Description"),
    dbc.Label("Card Fun Fact"),
    dbc.Input(id="card-fun-fact", type="text", placeholder="Insert Card Fun Fact"),
    html.Hr(),

    html.H2("Basic Properties"),
    dbc.Label("Card Level"),
    dbc.Input(id="card-level", type="number", min=1, max=3, step=1, value=1),
    dbc.Label("Card Cost"),
    dbc.Input(id="card-cost", type="number", min=0, max=1000, step=100, value=100),
    html.Hr(),

    html.H2("Rules"),
    dbc.Label("Player Reward"),
    dbc.Input(id="card-player-reward", type="number", min=0, step=1, value=0),
    dbc.Label("Target Reward"),
    dbc.Input(id="card-target-reward", type="number", min=0, step=1, value=0),

    dbc.Checklist(
        options=[
            {"label": "Is Multitarget?", "value": 0},
        ],
        value=[],
        id="card-is-multitarget",
        inline=True,
    ),
    html.Hr(),

    html.H2("Card Type and Coloring"),
    dbc.Select(
        id="card-type",
        value="0",
        options=[
            {"label": "General", "value": "0"},
            {"label": "Buff", "value": "1"},
            {"label": "Attack", "value": "2"},
            {"label": "Debuff", "value": "3"},
        ],
    ),
    html.Label("Background Texture"),
    dbc.Carousel(
        items=[
            {"key": meta, "src": image} for image, meta in zip(texture_images, texture_paths)
        ],
        controls=True,
        indicators=True,
        style={"width": "10vw"}
    ),
    html.Hr(),

    html.H2("Card Image"),
    dbc.Button("Open Card Image Creator", id="card-image-creator-btn"),
    image_creator,
    dcc.Upload("Select Card Image", id="card-image-upload"),
    dbc.Label("Card Image Filename"),
    dbc.Input(id="card-image-filename", type="text", placeholder="Insert Card Image Filename (Or Use Creator)"),
    html.Hr(),

    html.H2("Output"),
    dbc.Label("Card Save Filename"),
    dbc.Input(id="card-save-filename", type="text", placeholder="Insert Card Save Filename"),

])

card_preview = html.Div([
    html.Hr(),
    dbc.Button("Preview Card", id="card-preview-btn"),
    dbc.Button("Render Only This Card", id="card-render-one-btn"),
    dbc.Button("Render All Cards", id="card-render-all-btn"),
    html.Hr(),
    html.Img(id="card-preview-img", style={"height": "75vh"}),
], style={"position": "sticky", "top": 0, "height": "99vh"})

app.layout = dbc.Row([
    dbc.Col(width=1),
    dbc.Col(main_layout, width=4),
    dbc.Col(width=1),
    dbc.Col(card_preview, width=5),
    dbc.Col(width=1),
], style={"width": "99vw"})

# TODO: google image search
# TODO: image stylization
# TODO: card preview
# TODO: card save config/assets
# TODO: card type configurator + type texture/color mapping
# Define callback to update graph
@app.callback(
    Output('card-preview-img', 'src'),
    [Input("card-preview-btn", "n_clicks")]
)
def preview_card_callback(n_clicks):
    if n_clicks != None:
        with open("./card_maker_assets/data/hans.json", "r", encoding="utf-8") as fp:
            card = json.load(fp)
            card_src = cardmaker._render_card_to_png(card, show=False, save_path=None)
        return card_src
    return ""


@app.callback(
    Output("image-creator-modal", "is_open"),
    [Input("card-image-creator-btn", "n_clicks_timestamp"),
     Input("image-creator-save-btn", "n_clicks_timestamp")],
    State("image-creator-modal", "is_open"),
)
def image_creator_callback(open_btn_timestamp, save_btn_timestamp, is_open):
    if open_btn_timestamp is None:
        open_btn_timestamp = 0
    if save_btn_timestamp is None:
        save_btn_timestamp = 0
    if open_btn_timestamp > save_btn_timestamp:
        return True
    elif save_btn_timestamp > open_btn_timestamp:
        # Save button pressed
        print("save")
        return False
    return is_open


@app.callback(
    [Output("image-creator-search-results", "items"), Output("search-loading-output", "children")],
    Input("image-creator-search-btn", "n_clicks"),
    State("image-creator-search-input", "value")
)
def image_creator_search_callback(n_clicks, search_query):
    if n_clicks is not None:
        images, paths = cardmaker.search_images(search_query, n_results=30)
        return [{"key": path, "src": image} for path, image in zip(paths, images)], ""
    raise PreventUpdate


@app.callback(
    Output("image-creator-graph", "figure"),
    [Input("image-creator-search-results", "active_index"), Input("image-creator-style-select", "value"),
    State("image-creator-search-results", "items")]
)
def apply_image_style_callback(car_selection_index, style_selection, images):
    if car_selection_index is None:
        raise PreventUpdate
    img_path = images[car_selection_index]['key']
    return px.imshow(PIL.Image.open(img_path))

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True, port=8051)