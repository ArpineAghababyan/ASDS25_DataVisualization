import dash
from dash import html, dcc
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from pages.overview import layout as overview_layout
from pages.trends import layout as trends_layout
from pages.comparisons import layout as comparisons_layout

# Initializing the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX], suppress_callback_exceptions=True)
server = app.server

# Defining the navigation bar
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Overview", href="/overview")),
        dbc.NavItem(dbc.NavLink("Market Trends", href="/trends")),
        dbc.NavItem(dbc.NavLink("Price Comparisons", href="/comparisons")),
    ],
    brand="Polish Car Market Analysis Dashboard",
    brand_href="/overview",
    color="primary",
    dark=True,
    sticky="top",
)

# Defining the app layout
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', className="container mt-4"),])

# Callback for switching between pages
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/trends':
        return trends_layout
    elif pathname == '/comparisons':
        return comparisons_layout
    else:
        return overview_layout

if __name__ == '__main__':
    app.run(debug=True)