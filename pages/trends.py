from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from utils import load_and_clean_data

# Load and clean data
df = load_and_clean_data()
df = df[df['Production_year'].notna()]
price_min = 0
price_max = df["Price"].max()

layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H2("Market Trends Analysis", className="my-3 text-center"), width=12)
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H5("Filters", className="card-title"),
                dcc.Dropdown(
                    id="fuel-type-dropdown",
                    options=[{'label': ft, 'value': ft} for ft in df["Fuel_type"].dropna().unique()],
                    multi=True,
                    placeholder="Select Fuel Type",
                    style={"marginBottom": "1rem"}
                ),
                dcc.RangeSlider(
                    id="price-slider",
                    min=price_min,
                    max=price_max,
                    value=[price_min, price_max],
                    marks={int(i): f"{int(i/1000)}k" for i in range(0, int(price_max), 50000)},
                    step=1000,
                    tooltip={"always_visible": False}
                ),
            ])
        ], className="mb-4 shadow-sm"), width=12)
    ]),

    dbc.Row([
        dbc.Col(dbc.Tabs([
            dbc.Tab(label="Listings Over Time", tab_id="listings"),
            dbc.Tab(label="Fuel Type Trends", tab_id="fuel"),
            dbc.Tab(label="Transmission Trends", tab_id="transmission"),
        ], id="trends-tabs", active_tab="listings"), width=12)
    ]),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                dcc.Loading(dcc.Graph(id="trend-chart", config={"displayModeBar": False}))
            ])
        ], className="shadow-sm"), width=12)
    ])
], fluid=True)


@callback(
    Output("trend-chart", "figure"),
    Input("trends-tabs", "active_tab"),
    Input("fuel-type-dropdown", "value"),
    Input("price-slider", "value")
)
def update_trend_chart(active_tab, selected_fuels, price_range):
    filtered_df = df[
        (df["Price"] >= price_range[0]) & (df["Price"] <= price_range[1])
    ]
    if selected_fuels:
        filtered_df = filtered_df[filtered_df["Fuel_type"].isin(selected_fuels)]

    if active_tab == "listings":
        listings = filtered_df.groupby("Production_year").size().reset_index(name="Number_of_Listings")
        fig = px.line(listings, x="Production_year", y="Number_of_Listings",
                      title="Number of Listings Over Time")
    elif active_tab == "fuel":
        fuel_trends = filtered_df[filtered_df["Fuel_type"].notna()].groupby(
            ["Production_year", "Fuel_type"]
        ).size().reset_index(name="Count")
        fig = px.line(fuel_trends, x="Production_year", y="Count", color="Fuel_type",
                      title="Fuel Type Trends by Production Year")
    elif active_tab == "transmission":
        trans_trends = filtered_df[filtered_df["Transmission"].notna()].groupby(
            ["Production_year", "Transmission"]
        ).size().reset_index(name="Count")
        fig = px.line(trans_trends, x="Production_year", y="Count", color="Transmission",
                      title="Transmission Type Trends by Production Year")
    else:
        fig = px.line(title="No chart selected")

    fig.update_layout(margin=dict(l=40, r=20, t=60, b=40))
    return fig
