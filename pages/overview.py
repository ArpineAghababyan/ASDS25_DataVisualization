from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.express as px
from utils import load_and_clean_data, prepare_brand_data, prepare_color_data

# Load and preprocess data
df = load_and_clean_data()
avg_price_brand = prepare_brand_data(df)
color_counts = prepare_color_data(df)

# Calculate percentage of used vehicles
used_count = df[df['Condition'] == 'Used'].shape[0]
total_count = df.shape[0]
used_percentage = round((used_count / total_count) * 100, 1)  # rounded to 1 decimal place

# Chart 1: Average Price by Brand
brand_bar = px.bar(
    avg_price_brand,
    x="Vehicle_brand",
    y="Price",
    title="Average Car Price by Brand",
    color="Vehicle_brand",  # consistent categorical coloring
    color_discrete_sequence=px.colors.qualitative.Plotly
)
brand_bar.update_layout(xaxis_tickangle=-45)

# Chart 2: Condition Distribution
condition_pie = px.pie(
    df,
    names='Condition',
    title='Condition of Cars (New vs Used)',
    color_discrete_sequence=px.colors.qualitative.Plotly
)

# Chart 3: Color Popularity
color_bar = px.bar(
    color_counts,
    x='Colour',
    y='Count',
    title='Top 10 Most Popular Car Colors',
    color='Colour',
    color_discrete_sequence=px.colors.qualitative.Plotly
)

# Layout
layout = html.Div([
    dbc.Row([
        dbc.Col(html.H2("Car Market Overview"), width=12),
        dbc.Col(html.P(
            "An analysis of the Polish car market, comprising of analysis based on 200,000 car offers from one of the largest car advertisement sites in Poland."
        ), width=12),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=brand_bar), md=8),
        dbc.Col(dcc.Graph(figure=condition_pie), md=4),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=color_bar), width=12),
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col(html.Div([
            html.H4("Key Insights"),
            html.Ul([
                html.Li("Premium brands like Cupra and Maserati command the highest average prices"),
                html.Li("Black and white are the most popular car colors"),
                html.Li(f"The dataset contains mostly used vehicles ({used_percentage}%) with some new models"),
            ])
        ]), width=12),
    ]),
])
