"""Data cleaning for the CropVison project."""

import numpy as np
import pandas as pd


MESSY_DATA_FILE = "dataset/messy_up_crop.csv"
CLEAN_DATA_FILE = "dataset/clean_up_crop.csv"


def clean_data() -> pd.DataFrame:
    """Clean the messy CSV using Pandas and NumPy and return the cleaned data."""
    data = pd.read_csv(MESSY_DATA_FILE)
    data.columns = data.columns.str.strip()

    for column in ["State", "District", "Crop", "Year", "Season", "Area Units", "Production Units"]:
        if column in data.columns:
            data[column] = data[column].astype("string").str.strip()

    for column in ["State", "District", "Crop", "Season"]:
        if column in data.columns:
            data[column] = data[column].str.upper()

    data["YearNumber"] = data["Year"].str.extract(r"(\d{4})", expand=False)
    data["YearNumber"] = pd.to_numeric(data["YearNumber"], errors="coerce")

    for column in ["Area", "Production", "Yield"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data = data.drop_duplicates()
    data = data.dropna(subset=["District", "Crop", "Season", "YearNumber", "Area", "Yield"])

    valid = np.array(
        (data["Area"].to_numpy() > 0)
        & (data["Yield"].to_numpy() >= 0)
    )
    data = data.loc[valid].copy()

    # Remove extreme values using the IQR outlier rule.
    for column in ["Area", "Production", "Yield"]:
        values = pd.to_numeric(data[column], errors="coerce")
        values = values.dropna()
        if len(values) == 0:
            continue

        first_quartile = values.quantile(0.25)
        third_quartile = values.quantile(0.75)
        iqr = third_quartile - first_quartile
        lower_limit = first_quartile - 1.5 * iqr
        upper_limit = third_quartile + 1.5 * iqr

        keep = pd.to_numeric(data[column], errors="coerce")
        keep = keep.isna() | ((keep >= lower_limit) & (keep <= upper_limit))
        data = data.loc[keep].copy()

    data.to_csv(CLEAN_DATA_FILE, index=False)
    return data
