from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
from utils import load_and_clean_data, prepare_mileage_price_data, prepare_top_brands_data, prepare_deviation_data

df = load_and_clean_data()
df_clean_95 = df[df["Price"] < df["Price"].quantile(0.95)]

used_cars = prepare_mileage_price_data(df, condition='Used')
top_brands_df = prepare_top_brands_data(df)
deviation_data = prepare_deviation_data(df)

# Static plot (non-filtered)
avg_price_by_year = df_clean_95.groupby("Production_year")["Price"].mean().reset_index()
avg_price_fig = px.line(avg_price_by_year, x="Production_year", y="Price", title="Average Price by Production Year")

# Tabs layout
layout = html.Div([
    dbc.Row([dbc.Col(html.H2("Price Comparisons"), width=12)]),

    dbc.Tabs([
        dbc.Tab(label="Mileage vs Price", children=[
            dbc.Row([dbc.Col(dcc.Graph(id="mileage-scatter"), width=12)]),
        ]),

        dbc.Tab(label="Brand Comparisons", children=[
            dbc.Row([dbc.Col(dcc.Graph(id="price-box"), width=12)]),
        ]),

        dbc.Tab(label="Price Deviation", children=[
            dbc.Row([dbc.Col(dcc.Graph(id="deviation-scatter"), width=12)]),
        ]),

        dbc.Tab(label="Average Price by Year", children=[
            dbc.Row([dbc.Col(dcc.Graph(figure=avg_price_fig), width=12)]),
        ]),

        dbc.Tab(label="Price by Country of Origin", children=[
            dbc.Row([dbc.Col(dcc.Graph(id="country-origin-box"), width=12)]),
        ]),

        dbc.Tab(label="Animated Price vs Mileage", children=[
            dbc.Row([dbc.Col(dcc.Graph(id="animated-scatter"), width=12)]),
        ]),
    ]),

    # Filters
    dbc.Row([
        dbc.Col(html.Div([
            html.H4("Interactive Filters"),
            dcc.Dropdown(
                id='fuel-type-filter',
                options=[{'label': ft, 'value': ft} for ft in df['Fuel_type'].dropna().unique()],
                multi=True,
                placeholder="Filter by fuel type..."
            ),
            dcc.RangeSlider(
                id='price-range-slider',
                min=0,
                max=df['Price'].max(),
                value=[0, df['Price'].max()],
                marks={i: f"{int(i/1000)}k" for i in range(0, int(df['Price'].max()) + 1, 50000)},
                step=1000,
                tooltip={"placement": "bottom", "always_visible": False}
            ),
        ]), width=12),
    ])
])

# Callbacks
@callback(
    Output("mileage-scatter", "figure"),
    Output("price-box", "figure"),
    Output("deviation-scatter", "figure"),
    Output("country-origin-box", "figure"),
    Output("animated-scatter", "figure"),
    Input("fuel-type-filter", "value"),
    Input("price-range-slider", "value"),
)
def update_graphs(selected_fuels, price_range):
    filtered_df = df_clean_95.copy()

    if selected_fuels:
        filtered_df = filtered_df[filtered_df['Fuel_type'].isin(selected_fuels)]

    filtered_df = filtered_df[(filtered_df['Price'] >= price_range[0]) & (filtered_df['Price'] <= price_range[1])]

    # Graphs
    mileage_scatter = px.scatter(
        filtered_df[filtered_df["Condition"] == "Used"],
        x="Mileage_km", y="Price",
        color="Vehicle_brand",
        hover_data=["Vehicle_model", "Production_year"],
        title="Used Car Price vs Mileage"
    )

    box = px.box(
        filtered_df[filtered_df['Vehicle_brand'].isin(
            filtered_df['Vehicle_brand'].value_counts().nlargest(10).index)],
        x="Vehicle_brand",
        y="Price",
        color="Condition",
        title="Price Distribution by Top 10 Car Brands"
    )

    deviation = px.scatter(
        filtered_df,
        x="Mileage_km",
        y="%_Deviation" if "%_Deviation" in filtered_df.columns else "Price",
        color="Vehicle_brand",
        title="Price Deviation by Mileage and Brand"
    )

    country_origin = px.box(
        filtered_df[filtered_df['Origin_country'].notna()],
        x='Origin_country',
        y='Price',
        title='Car Price by Country of Origin'
    )

    animated = px.scatter(
        filtered_df[(filtered_df['Condition'] == 'Used') & filtered_df['Power_HP'].notna()],
        x="Mileage_km", y="Price",
        animation_frame="Production_year",
        animation_group="Vehicle_model",
        size="Power_HP",
        color="Vehicle_brand",
        hover_name="Vehicle_model",
        log_y=True,
        range_x=[0, filtered_df['Mileage_km'].max()],
        range_y=[100, filtered_df['Price'].max()],
        title="Used Car Price vs Mileage Over the Years"
    )

    return mileage_scatter, box, deviation, country_origin, animated
