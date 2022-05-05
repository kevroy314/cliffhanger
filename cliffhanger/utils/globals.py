"""Global variables for visualization and across the app."""
data_location = './data'
log_location = './logs'

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

party_bac_failure_threshold = 0.08
