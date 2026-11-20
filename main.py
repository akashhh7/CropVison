"""CropVison: a beginner-friendly terminal crop production and yield predictor."""

import numpy as np
import pandas as pd


MESSY_DATA_FILE = "dataset/messy_up_crop.csv"
CLEAN_DATA_FILE = "dataset/clean_up_crop.csv"


def clean_data() -> pd.DataFrame:
    """Clean the messy CSV using Pandas and NumPy."""
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


def predict_yield(data: pd.DataFrame, district: str, crop: str, season: str) -> tuple[float, str]:
    """Estimate yield using the historical average for the entered details."""
    exact = data[
        (data["District"] == district)
        & (data["Crop"] == crop)
        & (data["Season"] == season)
    ]
    if len(exact) > 0:
        return float(exact["Yield"].mean()), "district, crop and season average"

    crop_season = data[(data["Crop"] == crop) & (data["Season"] == season)]
    if len(crop_season) > 0:
        return float(crop_season["Yield"].mean()), "crop and season average"

    crop_only = data[data["Crop"] == crop]
    if len(crop_only) > 0:
        return float(crop_only["Yield"].mean()), "crop average"

    return float(data["Yield"].mean()), "overall average"


def ask_choice(prompt: str, choices: list[str]) -> str:
    """Ask until the user enters a value from the available choices."""
    choice_map = {choice.lower(): choice for choice in choices}

    while True:
        answer = input(prompt).strip().lower()
        if answer in choice_map:
            return choice_map[answer]
        print("Invalid choice. Please use one of the values shown below.")


def ask_positive_number(prompt: str) -> float:
    """Ask until the user enters a positive number."""
    while True:
        try:
            number = float(input(prompt).strip())
            if number > 0:
                return number
            print("Please enter a number greater than zero.")
        except ValueError:
            print("Please enter a valid number.")


def ask_year() -> int:
    """Ask until the user enters a reasonable four-digit year."""
    while True:
        try:
            year = int(input("Year (for example 2025): ").strip())
            if 1900 <= year <= 2100:
                return year
            print("Please enter a year from 1900 to 2100.")
        except ValueError:
            print("Please enter a valid year.")


def main():
    print("========================================")
    print("       CropVison Yield Predictor")
    print("========================================")

    data = clean_data()

    districts = sorted(data["District"].dropna().unique())
    crops = sorted(data["Crop"].dropna().unique())
    seasons = sorted(data["Season"].dropna().unique())

    print("\nAvailable districts:")
    print("  " + ", ".join(districts))
    district = ask_choice("\nDistrict: ", districts).upper()

    print("\nAvailable crops:")
    print("  " + ", ".join(crops))
    crop = ask_choice("Crop: ", crops).upper()

    print("\nAvailable seasons:")
    print("  " + ", ".join(seasons))
    season = ask_choice("Season: ", seasons).upper()

    year = ask_year()
    area = ask_positive_number("Area in hectares: ")

    yield_prediction, estimate_used = predict_yield(data, district, crop, season)
    production_prediction = yield_prediction * area

    print("\n========================================")
    print("               Prediction")
    print("========================================")
    print(f"District:   {district.title()}")
    print(f"Crop:       {crop.title()}")
    print(f"Season:     {season.title()}")
    print(f"Year:       {year}")
    print(f"Area:       {area:.2f} hectares")
    print(f"Estimate:   {estimate_used}")
    print(f"Yield:      {yield_prediction:.2f} tonnes/hectare")
    print(f"Production: {production_prediction:.2f} tonnes")


if __name__ == "__main__":
    main()
