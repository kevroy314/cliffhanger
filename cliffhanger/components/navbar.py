import dash_bootstrap_components as dbc


def create_navbar(pages):
    dropdown_options = []
    for page in pages:
        if page is None:
            dropdown_options.append(dbc.DropdownMenuItem(divider=True))
        elif page.show_in_navbar:
            dropdown_options.append(dbc.DropdownMenuItem(page.display_name, href=page.url))

    navbar = dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                nav=True, in_navbar=True, label="Menu",
                children=dropdown_options,
            ),
        ],
        brand="Home", brand_href="/", sticky="top", color="dark", dark=True,
    )

    return navbar
