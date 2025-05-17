import os
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.express as px


def get_data_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(current_dir, 'data', 'ArpineA_data.csv')
    return data_path


def load_and_clean_data():
    data_path = get_data_path()
    print(f"Loading data from: {data_path}")  # Debug print

    try:
        df = pd.read_csv(data_path)
    except Exception as e:
        raise Exception(f"Error loading data file: {str(e)}")

    # Handle data types
    df['Offer_publication_date'] = pd.to_datetime(
        df['Offer_publication_date'],
        format='%d/%m/%Y',
        errors='coerce'
    )
    df['First_registration_date'] = pd.to_datetime(
        df['First_registration_date'],
        format='%d/%m/%Y',
        errors='coerce'
    )

    # Clean data (keep 95th percentile)
    numeric_cols = df.select_dtypes(include='number').columns
    percentiles = df[numeric_cols].quantile(0.95)
    df_clean_95 = df.copy()
    for col in numeric_cols:
        df_clean_95 = df_clean_95[df_clean_95[col] <= percentiles[col]]

    # Additional processing
    df_clean_95['Car_Age'] = 2025 - df_clean_95['Production_year']

    return df_clean_95


def prepare_brand_data(df):
    """Prepare brand price data for visualization"""
    return df.groupby("Vehicle_brand")["Price"].mean().sort_values(ascending=False).reset_index()


def prepare_mileage_price_data(df, condition=None):
    """Filter data for mileage vs price analysis"""
    if condition:
        return df[df['Condition'] == condition]
    return df


def prepare_engine_data(df):
    """Filter data for engine analysis"""
    return df[df['Displacement_cm3'].notna() & df['Power_HP'].notna()]


def prepare_top_brands_data(df, n=10):
    """Get data for top n brands by frequency"""
    top_brands = df['Vehicle_brand'].value_counts().nlargest(n).index
    return df[df['Vehicle_brand'].isin(top_brands)]


def prepare_price_trend_data(df):
    """Prepare data for price trend analysis"""
    return df.groupby("Production_year")["Price"].mean().reset_index()


def prepare_color_data(df, n=10):
    """Prepare data for color popularity analysis"""
    color_counts = df['Colour'].value_counts().nlargest(n).reset_index()
    color_counts.columns = ['Colour', 'Count']
    return color_counts


def prepare_origin_data(df, condition=None):
    """Prepare data for origin country analysis"""
    if condition:
        return df[(df['Condition'] == condition) & (df['Origin_country'].notna())]
    return df[df['Origin_country'].notna()]


def prepare_animation_data(df):
    """Prepare data for animated visualizations"""
    df_anim = df[(df['Condition'] == 'Used') &
                 df['Power_HP'].notna() &
                 df['Production_year'].notna()].copy()
    df_anim['Power_HP'] = df_anim['Power_HP'].astype(float)
    df_anim['Bubble_Size'] = df_anim['Power_HP'] / df_anim['Power_HP'].max() * 50
    return df_anim


def prepare_deviation_data(df, by_model=False):
    """
    Prepare data for price deviation analysis
    Args:
        df: Input dataframe
        by_model: Whether to group by model in addition to brand and year
    """
    if by_model:
        group_cols = ["Vehicle_brand", "Vehicle_model", "Production_year"]
    else:
        group_cols = ["Vehicle_brand", "Production_year"]

    median_df = df.groupby(group_cols)["Price"].median().reset_index()
    median_df.rename(columns={"Price": "Price_median"}, inplace=True)

    df_deviation = df.merge(median_df, on=group_cols, how="left")
    df_deviation['Price_deviation'] = df_deviation['Price'] - df_deviation['Price_median']
    df_deviation['%_Deviation'] = (df_deviation['Price_deviation'] / df_deviation['Price_median']) * 100

    return df_deviation


def get_brand_options(df):
    """Get brand options for dropdowns"""
    brands = df['Vehicle_brand'].unique()
    return [{'label': brand, 'value': brand} for brand in sorted(brands)]


def get_fuel_type_options(df):
    """Get fuel type options for dropdowns"""
    fuel_types = df['Fuel_type'].unique()
    return [{'label': ft, 'value': ft} for ft in sorted(fuel_types) if pd.notna(ft)]


def get_year_range(df):
    """Get min and max production years"""
    return {
        'min': int(df['Production_year'].min()),
        'max': int(df['Production_year'].max())
    }