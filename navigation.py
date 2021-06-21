import dash_bootstrap_components as dbc
import dash_html_components as html

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/home")),
        dbc.NavItem(dbc.NavLink("Model", href="/model")),
        dbc.NavItem(dbc.NavLink("Team", href="/team")),
    ],
    brand="Social Media Health Organization",
    brand_href="#",
    color="dark",
    dark=True,
)