from re import L
from distutils.command.upload import upload
from itsdangerous import base64_decode
from tokenize import blank_re
from ctypes import alignment, resize
import os
import uuid
import PIL
import base64
import json
import plotly.express as px
import dash
from datetime import datetime
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import cardmaker
from PIL import Image, ImageFilter, ImageDraw
from skimage.segmentation import slic
from skimage.feature import corner_peaks, corner_fast
from skimage.color import rgb2gray, label2rgb
from scipy.spatial import Delaunay
import numpy as np

app = dash.Dash(__name__,  external_stylesheets=[dbc.themes.SLATE], assets_folder="./card_maker_assets")

texture_path = './card_maker_assets/textures'
texture_images, texture_paths = cardmaker.load_images_as_b64(texture_path, include_paths=True)
DT_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

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
                style={"width": "50vw", "margin-left": "25vw"},
            ),
            dbc.Select(
                id="image-creator-style-select",
                value="0",
                options=[
                    {"label": "Original Style", "value": "0"},
                    {"label": "Triangulation Style", "value": "1"},
                    {"label": "Blur and Quantize", "value": "2"},
                    {"label": "Cluster", "value": "3"}
                ],
            ),
            html.Label("", id="tweak-0-label"),
            dcc.Slider(0, 1, 0.1, id="tweak-0-slider", disabled=True),
            html.Label("", id="tweak-1-label"),
            dcc.Slider(0, 1, 0.1, id="tweak-1-slider", disabled=True),
            dcc.Graph(id="image-creator-graph"),
            dbc.Button("Crop to View and Save", id="image-creator-save-btn"),
        ]),
    ],
    id="image-creator-modal",
    fullscreen=True,
)

card_type_options = [
    {"label": "General", "value": "0"},
    {"label": "Buff", "value": "1"},
    {"label": "Attack", "value": "2"},
    {"label": "Debuff", "value": "3"},
]

texture_items = [
    {"key": meta, "src": image} for image, meta in zip(texture_images, texture_paths)
]

main_layout = html.Div([
    html.H1("Cardmaker"),
    html.Hr(),
    html.H2("Card Save/Load"),
    dcc.Upload(dbc.Button("Open Card"), accept='application/json', id="open-card-upload"),
    dbc.Input(id="save-filename", type="text"),
    dbc.Button("Save Card", id="save-card-btn"),
    dcc.Download(id="save-selection"),
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
        options=card_type_options,
    ),
    html.Label("Background Texture"),
    dbc.Carousel(
        id="texture-select",
        items=texture_items,
        active_index=0,
        controls=True,
        indicators=True,
        style={"width": "10vw"}
    ),
    html.Hr(),

    html.H2("Card Image"),
    dbc.Button("Create Image in Built-In Creator", id="card-image-creator-btn"),
    image_creator,
    dcc.Upload(dbc.Button("Upload Custom Image"), id="card-image-upload"),
    dbc.Label("Card Image Filename"),
    dbc.Input(id="card-image-filename", type="text", placeholder="Insert Card Image Filename (Or Use Creator)"),
    dbc.Input(id="card-image-filename-dt", type="text", style={"display": "none"}),
    dbc.Input(id="card-image-filename-from-json-dt", type="text", style={"display": "none"}),
    dbc.Input(id="card-image-filename-from-json", type="text", style={"display": "none"}),
    dbc.Input(id="card-image-filename-from-creators-dt", type="text", style={"display": "none"}),
    dbc.Input(id="card-image-filename-from-creators", type="text", style={"display": "none"}),
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


save_load_state_fields = [
    ("card-name", "value"),
    ("card-description", "value"),
    ("card-fun-fact", "value"),
    ("card-level", "value"),
    ("card-cost", "value"),
    ("card-player-reward", "value"),
    ("card-target-reward", "value"),
    ("card-is-multitarget", "value"),
    ("card-type", "value"),
    ("texture-select", "active_index"),
    ("card-image-filename-from-json", "value"),
    ("card-image-filename-from-json-dt", "value")
]

# TODO: card save forces page refresh
# TODO: card save config/assets
# TODO: card type configurator + type texture/color mapping
@app.callback(
    Output('card-preview-img', 'src'),
    [Input("card-preview-btn", "n_clicks")],
    [State('card-image-filename', 'value')] + [State(identifier, member) for identifier, member in save_load_state_fields]
)
def preview_card_callback(n_clicks, card_image_filename, *state_args):
    card = transform_state_args_to_dict(card_image_filename, state_args)
    transformed_card = {}
    for key in card:
        if "json" not in key:
            transformed_card[key.replace('card-', '').replace("-select", "").replace("card_", "").replace("_filename", "")] = card[key]
    if n_clicks != None:
        card_src = cardmaker._render_card_to_png(transformed_card, show=False, save_path=None, prepend_paths=False)
        return card_src
    return ""


@app.callback(
    [Output("image-creator-modal", "is_open"), Output("card-image-filename-from-creators", "value"), Output("card-image-filename-from-creators-dt", "value")],
    [Input("card-image-creator-btn", "n_clicks_timestamp"),
     Input("image-creator-save-btn", "n_clicks_timestamp"),
     Input("card-image-upload", "contents"),
     Input("card-image-upload", "filename")],
    [State("image-creator-modal", "is_open"),
     State("image-creator-graph", "figure"),
     State("card-image-filename-from-creators", "value"),
     State("card-image-filename-from-creators-dt", "value")],
)
def image_creator_callback(open_btn_timestamp, save_btn_timestamp, image_content, image_filename, is_open, figure, prev_filename, prev_datetime):
    button_pressed = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if button_pressed == "card-image-upload.filename" or button_pressed == "card-image-upload.contents":
        image_save_name = str(uuid.uuid4())
        new_filename = f"./card_maker_assets/images/{image_save_name}.png"
        tmp_filename = image_save_name+image_filename
        _, content_string = image_content.split(',')
        with open(tmp_filename, "wb") as fp:
            fp.write(base64.b64decode(content_string))
        img = PIL.Image.open(tmp_filename)
        os.remove(tmp_filename)
        img.save(new_filename)
        prev_filename = new_filename
        prev_datetime = datetime.now().strftime(DT_FORMAT)
    if open_btn_timestamp is None:
        open_btn_timestamp = 0
    if save_btn_timestamp is None:
        save_btn_timestamp = 0
    if open_btn_timestamp > save_btn_timestamp:
        return True, prev_filename, prev_datetime
    elif save_btn_timestamp > open_btn_timestamp:
        # Save button pressed
        blank_img = PIL.Image.open("blank_image.png")
        fig = go.Figure(figure)
        fig.update_layout(autosize=False, width=blank_img.width, height=blank_img.height,
                          margin={'l': 0, 'r': 0, 't': 0, 'b': 0})
        fig.write_image("tmp.png", width=blank_img.width, height=blank_img.height, scale=5.0)
        img = PIL.Image.open("tmp.png")
        img = img.crop((878, 550, 878+1044, 550+655))
        img = img.resize((blank_img.width, blank_img.height))
        os.remove("tmp.png")
        image_save_name = str(uuid.uuid4())
        new_filename = f"./card_maker_assets/images/{image_save_name}.png"
        img.save(new_filename)
        return False, new_filename, datetime.now().strftime(DT_FORMAT)
    return is_open, prev_filename, prev_datetime


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


def _blur_and_quantize(img, blur=5, quantize=16):
    blur = int(blur)
    quantize = int(quantize)
    img = img.filter(ImageFilter.GaussianBlur(radius=blur))
    img = img.quantize(quantize)
    return img

def _color_cluster(img, n_segments=100, compactness=1):
    n_segments = int(n_segments)
    compactness = int(compactness)
    image_array = np.asarray(img)
    segments = slic(image_array, n_segments=n_segments, compactness=compactness)
    img = Image.fromarray(label2rgb(segments, image_array, kind='avg', bg_label=0))
    return img

def _triangulation(img, n=12, threshold=0.15):
    n = int(n)
    image_array = np.asarray(img)
    gray_image = rgb2gray(image_array)

    points = [tuple([x[1], x[0]]) for x in corner_peaks(corner_fast(gray_image, n=n, threshold=threshold))]
    for i in range(0, img.width, int(img.width/4)):
        points.append((0, i))
        points.append((i, 0))
        points.append((img.height, i))
        points.append((i, img.height))
    for i in range(0, img.height, int(img.height/4)):
        points.append((0, i))
        points.append((i, 0))
        points.append((i, img.width))
        points.append((img.width, i))
    points.append((img.width, img.height))
    tri = Delaunay(points, incremental=True)
    draw_img = img.copy()
    draw = ImageDraw.Draw(draw_img)
    draw.rectangle([(0, 0), (draw_img.width, draw_img.height)], fill=(0, 0, 0))
    for a, b, c in tri.simplices:
        center = tuple(((np.array(points[a]).astype(float) + np.array(points[b]).astype(float) + np.array(points[c]).astype(float))/3.0).astype(int))
        center = (min(center[0], img.width-1), min(center[1], img.height-1))
        draw.polygon([points[a], points[b], points[c]], fill=img.getpixel(center))
    return draw_img


@app.callback(
    [Output("image-creator-graph", "figure"),
     Output("tweak-0-label", "children"),
     Output("tweak-1-label", "children"),
     Output("tweak-0-slider", "disabled"),
     Output("tweak-1-slider", "disabled"),
     Output("tweak-0-slider", "min"),
     Output("tweak-1-slider", "min"),
     Output("tweak-0-slider", "max"),
     Output("tweak-1-slider", "max"),
     Output("tweak-0-slider", "step"),
     Output("tweak-1-slider", "step"),
     Output("tweak-0-slider", "value"),
     Output("tweak-1-slider", "value")],
    [Input("image-creator-search-results", "active_index"),
     Input("image-creator-style-select", "value"),
     Input("image-creator-search-results", "items"),
     Input("tweak-0-slider", "value"),
     Input("tweak-1-slider", "value")]
)
def apply_image_style_callback(car_selection_index, style_selection, images, slider0, slider1):
    button_pressed = [p['prop_id'] for p in dash.callback_context.triggered][0]

    if images is None or len(images) == 0:
        raise PreventUpdate
    if car_selection_index is not None:
        img_path = images[car_selection_index]['key']
    else:
        img_path = images[0]['key']
    img = PIL.Image.open(img_path)
    tweak0, tweak1 = "", ""
    tweak0_disabled, tweak1_disabled = True, True
    min0, max0, step0 = 0, 1, 1
    min1, max1, step1 = 0, 1, 1
    if style_selection == "1":
        if button_pressed == "image-creator-style-select.value":
            slider0, slider1 = 12, 0.15
        img = _triangulation(img, n=slider0, threshold=slider1)
        tweak0, tweak1 = "N", "Threshold"
        tweak0_disabled, tweak1_disabled = False, False
        min0, max0, step0 = 0, 50, 1
        min1, max1, step1 = 0, 1, 0.05
    elif style_selection == "2":
        if button_pressed == "image-creator-style-select.value":
            slider0, slider1 = 5, 16
        img = _blur_and_quantize(img, blur=slider0, quantize=slider1)
        tweak0, tweak1 = "Blur Size", "Quantize Levels"
        tweak0_disabled, tweak1_disabled = False, False
        min0, max0, step0 = 1, 20, 1
        min1, max1, step1 = 1, 127, 2
    elif style_selection == "3":
        if button_pressed == "image-creator-style-select.value":
            slider0, slider1 = 100, 1
        img = _color_cluster(img, n_segments=slider0, compactness=slider1)
        tweak0, tweak1 = "N Segments", "Compactness"
        tweak0_disabled, tweak1_disabled = False, False
        min0, max0, step0 = 1, 500, 10
        min1, max1, step1 = 1, 50, 1
    blank_img = PIL.Image.open("blank_image.png")
    if img.width > blank_img.width:
        proportion = img.width / blank_img.width
        blank_img = blank_img.resize((img.width, int(proportion * blank_img.height)))
    if img.height > blank_img.height:
        proportion = img.height / blank_img.height
        blank_img = blank_img.resize((int(proportion * blank_img.width), img.height))
    fig = px.imshow(blank_img)
    fig.add_layout_image(
        dict(
            source=img,
            xref="x",
            yref="y",
            x=0,
            y=0,
            sizex=img.width,
            sizey=img.height,
            # sizing="stretch",
            opacity=1,
            layer="above")
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis={'showgrid': False},
        yaxis={'showgrid': False}
    )
    fig.update_layout(coloraxis_showscale=False)
    fig.update_xaxes(showticklabels=False)
    fig.update_yaxes(showticklabels=False)
    return fig, tweak0, tweak1, tweak0_disabled, tweak1_disabled, min0, min1, max0, max1, step0, step1, slider0, slider1


@app.callback(
    Output("card-image-filename", "value"),
    [Input("card-image-filename-from-json", "value"), Input("card-image-filename-from-creators", "value")],
    [State("card-image-filename-from-json-dt", "value"), State("card-image-filename-from-creators-dt", "value"), State("card-image-filename-dt", "value")],
)
def sync_image_filenames(from_json, from_creators, from_json_dt, from_creators_dt, original_dt):
    if from_creators_dt is None:
        from_creators_dt = datetime(1970, 1, 1, 0, 0, 0, 0)
    else:
        from_creators_dt = datetime.strptime(from_creators_dt, DT_FORMAT)
    if from_json_dt is None:
        from_json_dt = datetime(1970, 1, 1, 0, 0, 0, 0)
    else:
        from_json_dt = datetime.strptime(from_json_dt, DT_FORMAT)
    if original_dt is None:
        original_dt = datetime(1970, 1, 1, 0, 0, 0, 0)
    else:
        original_dt = datetime.strptime(original_dt, DT_FORMAT)
    
    max_val = max([from_creators_dt, from_json_dt, original_dt])
    ret_val = None
    if max_val == original_dt:
        ret_val = None
    if max_val == from_json_dt:
        ret_val = from_json
    if max_val == from_creators_dt:
        ret_val = from_creators
    if ret_val is None:
        raise PreventUpdate()
    else:
        return ret_val

@app.callback(
    Output("card-image-filename-dt", "value"),
    Input("card-image-filename", "value")
)
def card_image_manual_edit_timestamp(_):
    return datetime.now().strftime(DT_FORMAT)

def transform_state_args_to_dict(card_image_filename, state_args):
    export_dict = {}
    for idx, (identifier, _) in enumerate(save_load_state_fields):
        export_dict[identifier] = state_args[idx]
    export_dict['card-is-multitarget'] = int(export_dict['card-is-multitarget'] == [0])
    for option in card_type_options:
        if option["value"] == export_dict['card-type']:
            export_dict['card-type'] = option["label"]
    export_dict['texture-select'] = texture_items[export_dict['texture-select']]['key']
    export_dict['card_image_filename'] = card_image_filename
    return export_dict

def transform_dict_to_state_args(card_dict):
    card_dict['card-is-multitarget'] = [0] if card_dict['card-is-multitarget'] else []
    for option in card_type_options:
        if option["label"] == card_dict['card-type']:
            card_dict['card-type'] = option["value"]
    for idx, ti in enumerate(texture_items):
        if ti['key'] == card_dict['texture-select']:
            card_dict['texture-select'] = idx
    card_dict['card-image-filename-from-json'] = card_dict['card_image_filename']
    card_dict['card-image-filename-from-json-dt'] = datetime.now().strftime(DT_FORMAT)
    state_args_replacement = []
    for identifier, _ in save_load_state_fields:
        state_args_replacement.append(card_dict[identifier])
        state_args = tuple(state_args_replacement)    

    return state_args

@app.callback(
    [Output("save-selection", "data"), Output("save-filename", "value")]+[Output(identifier, member) for identifier, member in save_load_state_fields],
    [Input("open-card-upload", "filename"),
     Input("open-card-upload", "contents"),
     Input("save-card-btn", "n_clicks_timestamp")],
    [State('save-filename', 'value'), State('card-image-filename', 'value')] + [State(identifier, member) for identifier, member in save_load_state_fields],
    prevent_initial_call=True
)
def image_creator_search_callback(open_filename, open_contents, save_last_click, save_filename, card_image_filename, *state_args):
    button_pressed = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if button_pressed == "save-card-btn.n_clicks_timestamp":
        if save_filename is None:
            raise PreventUpdate()
        export_dict = transform_state_args_to_dict(card_image_filename, state_args)
        with open(save_filename, "w") as fp:
            json.dump(export_dict, fp, indent=4, sort_keys=True)
    else:
        save_filename = open_filename
        _, content_string = open_contents.split(',')
        json_data = json.loads(base64.b64decode(content_string).decode("utf-8"))
        state_args = transform_dict_to_state_args(json_data)
    return tuple([None, save_filename] + list(state_args))
    raise PreventUpdate()
    
    return dcc.send_file(
        "./dash_docs/assets/images/gallery/dash-community-components.png"
    )

if __name__ == '__main__':
    app.run_server(host="0.0.0.0", debug=True, port=8051)