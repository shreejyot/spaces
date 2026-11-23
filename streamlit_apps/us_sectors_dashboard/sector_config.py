from pathlib import Path

import pandas as pd


SECTORS_FILE = Path(__file__).with_name("sectors.csv")
SECTOR_COLUMNS = ["Ticker", "Description", "AssetClass"]


def validate_sectors(dataframe):
    if list(dataframe.columns) != SECTOR_COLUMNS:
        raise ValueError("The sector table must contain Ticker, Description, and AssetClass columns.")

    sectors = dataframe.copy()
    for column in SECTOR_COLUMNS:
        sectors[column] = sectors[column].fillna("").astype(str).str.strip()
    sectors["Ticker"] = sectors["Ticker"].str.upper()

    if sectors.empty:
        raise ValueError("Add at least one sector before saving.")
    if (sectors == "").any().any():
        raise ValueError("Ticker and Description values cannot be blank.")
    if sectors["Ticker"].duplicated().any():
        raise ValueError("Each ticker must be unique.")
    if sectors["Ticker"].eq("SPY").any():
        raise ValueError("SPY is reserved for the benchmark and cannot be added as a sector.")

    return sectors


def load_sectors_dataframe(path=SECTORS_FILE):
    return validate_sectors(pd.read_csv(path))


def load_sectors(path=SECTORS_FILE):
    sectors = load_sectors_dataframe(path)
    return dict(zip(sectors["Ticker"], sectors["Description"]))


def save_sectors_dataframe(dataframe, path=SECTORS_FILE):
    sectors = validate_sectors(dataframe)
    sectors.to_csv(path, index=False)
