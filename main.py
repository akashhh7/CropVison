"""CropVison: a beginner-friendly terminal crop production and yield predictor."""

import pandas as pd

from data_cleaning import clean_data


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
    area = ask_positive_number("Area(in hectares): ")

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
