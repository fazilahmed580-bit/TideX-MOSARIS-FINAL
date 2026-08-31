import pandas as pd
import numpy as np

def clean_ais(data):
    """
    Load and clean NOAA AIS data.
    """

    if isinstance(data, str):
        df = pd.read_csv(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise ValueError("data must be a pandas DataFrame or a file path")

    # Rename NOAA AIS columns to the names used by TideX
    col_mapping = {
        'base_date_time': 'timestamp',
        'sog': 'sog_knots',
        'cog': 'cog_deg',
        'heading': 'heading_deg'
    }

    df.rename(columns=col_mapping, inplace=True)

    required_cols = [
        'mmsi',
        'vessel_name',
        'timestamp',
        'latitude',
        'longitude',
        'sog_knots',
        'cog_deg',
        'heading_deg'
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Timestamp
    df['timestamp'] = pd.to_datetime(
        df['timestamp'],
        utc=True,
        errors='coerce'
    )

    df = df.dropna(subset=['timestamp'])

    # MMSI
    df['mmsi'] = pd.to_numeric(
        df['mmsi'],
        errors='coerce'
    )

    df = df.dropna(subset=['mmsi'])
    df = df[df['mmsi'] > 0]

    # Vessel name
    df['vessel_name'] = (
        df['vessel_name']
        .fillna("UNKNOWN")
        .astype(str)
    )

    # Latitude / longitude
    df['latitude'] = pd.to_numeric(
        df['latitude'],
        errors='coerce'
    )

    df['longitude'] = pd.to_numeric(
        df['longitude'],
        errors='coerce'
    )

    df = df.dropna(subset=['latitude', 'longitude'])

    df = df[
        (df['latitude'] >= -90) &
        (df['latitude'] <= 90) &
        (df['longitude'] >= -180) &
        (df['longitude'] <= 180)
    ]

    # Speed
    df['sog_knots'] = pd.to_numeric(
        df['sog_knots'],
        errors='coerce'
    )

    df = df.dropna(subset=['sog_knots'])

    df = df[
        (df['sog_knots'] >= 0) &
        (df['sog_knots'] <= 200)
    ]

    # COG
    df['cog_deg'] = pd.to_numeric(
        df['cog_deg'],
        errors='coerce'
    )

    # Heading
    df['heading_deg'] = pd.to_numeric(
        df['heading_deg'],
        errors='coerce'
    )

    def normalize_angle(x):
        if pd.isna(x) or x == 511:
            return np.nan
        return x % 360

    df['cog_deg'] = df['cog_deg'].apply(normalize_angle)
    df['heading_deg'] = df['heading_deg'].apply(normalize_angle)

    # Remove duplicate AIS observations
    df = df.drop_duplicates(
        subset=['mmsi', 'timestamp']
    )

    # Sort chronologically
    df = df.sort_values(
        by=['mmsi', 'timestamp']
    ).reset_index(drop=True)

    return df