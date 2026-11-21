# CropVison

A python project using NumPy and Pandas for Uttar Pradesh crop yield and production estimation.

## Project files

- `main.py` — terminal interface and yield/production calculation
- `data_cleaning.py` — CSV loading, cleaning, validation and IQR outlier removal
- `dataset/messy_up_crop.csv` — original data
- `dataset/clean_up_crop.csv` — cleaned data created when the program runs

## Setup

Install dependencies:

```bash
python -m pip install numpy pandas
```

## Run
```bash
1. python data_cleaning.py
```
Cleans the messy csv file data and creates a new cleaned csv file. 

```bash
2. python main.py
```

Enter the district, crop, season, year and cultivated area when prompted.

`data_cleaning.py` uses Pandas and NumPy to load, clean and filter the CSV. `main.py` handles the terminal interface and historical-average estimation.

Outliers are removed using the IQR rule for area, production and yield:

- Lower limit = Q1 − 1.5 × IQR
- Upper limit = Q3 + 1.5 × IQR

Values outside these limits are not written to the cleaned CSV.

Yield is estimated from the historical average for the matching district, crop and season. Production is calculated as:

`production = estimated yield × area in hectares`

