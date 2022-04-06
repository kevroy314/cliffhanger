import dash_bootstrap_components as dbc


def create_navbar(pages):
    dropdown_options = []
    for page in pages:
        if page is None:
            dropdown_options.append(dbc.DropdownMenuItem(divider=True, className="dropdown-divider"))
        elif page.show_in_navbar:
            dropdown_options.append(dbc.DropdownMenuItem(page.display_name, href=page.url, className="dropdown-item"))

    navbar = dbc.NavbarSimple(
        children=dropdown_options,
        brand="Cliffhanger", brand_href="/", brand_style={"margin-left": "10px"}, sticky="top", color="dark", dark=True,
    )

    return navbar
