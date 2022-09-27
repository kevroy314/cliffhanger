"""Global variables for visualization and across the app."""
import os

DATA_LOCATION = './data'
LOG_LOCATION = './logs'

drinks_cat_lut = {
    1: "Nothing",
    2: "Beer",
    3: "Wine",
    4: "Liquor (Drinks)",
    5: "Liquor (Shots)"
}

drinks_color_lut = {
    "Nothing": "#0F0E0E",
    "Beer": "#f28e1c",
    "Wine": "#BA091E",
    "Liquor (Drinks)": "#ADD8E6",
    "Liquor (Shots)": "#2364AA"
}

if not os.path.exists(DATA_LOCATION):
    os.mkdir(DATA_LOCATION)
if not os.path.exists(LOG_LOCATION):
    os.mkdir(LOG_LOCATION)
if not os.path.exists("./assets/qrcodes"):
    os.mkdir("./assets/qrcodes")
