
import dash_bootstrap_components as dbc


def create_navbar(pages):
    navbar = dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                nav=True, in_navbar=True, label="Menu",
                children=[dbc.DropdownMenuItem(divider=True) if page is None else dbc.DropdownMenuItem(page.display_name, href=page.url) for page in pages],
            ),
        ],
        brand="Home", brand_href="/", sticky="top", color="dark", dark=True,
    )

    return navbar
