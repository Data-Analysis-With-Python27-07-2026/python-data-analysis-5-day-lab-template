from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


def repo_root(start: Path | None = None) -> Path:
    current = (start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "notebooks").exists() and (candidate / "scripts").exists():
            return candidate
    raise FileNotFoundError("Repository root could not be located.")


def ensure_data(rows: int = 50000) -> Path:
    root = repo_root()
    path = root / "data" / "flights_sample.csv"
    if not path.exists():
        subprocess.run(
            [sys.executable, str(root / "scripts" / "prepare_data.py"), "--rows", str(rows), "--allow-fallback"],
            check=True,
            cwd=root,
        )
    return path


def load_flights(rows: int = 50000) -> pd.DataFrame:
    return pd.read_csv(ensure_data(rows), low_memory=False)


def data_source() -> dict:
    root = repo_root()
    path = root / "data" / "DATA_SOURCE.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"source": "unknown"}


def hhmm_to_hour(value) -> float:
    if pd.isna(value):
        return float("nan")
    try:
        value = int(float(value))
    except (TypeError, ValueError):
        return float("nan")
    hour = value // 100
    return float(hour if 0 <= hour <= 23 else "nan")


def clean_flights(df: pd.DataFrame) -> pd.DataFrame:
    clean = df.drop_duplicates().copy()
    clean["FLIGHT_DATE"] = pd.to_datetime(
        dict(year=clean["YEAR"], month=clean["MONTH"], day=clean["DAY"]),
        errors="coerce",
    )
    clean["SCHEDULED_HOUR"] = clean["SCHEDULED_DEPARTURE"].apply(hhmm_to_hour)
    clean["DELAYED_15"] = clean["DEPARTURE_DELAY"].gt(15).fillna(False)
    clean["ARRIVAL_DELAYED_15"] = clean["ARRIVAL_DELAY"].gt(15).fillna(False)
    reason_map = {"A": "Airline/Carrier", "B": "Weather", "C": "National Air System", "D": "Security"}
    clean["CANCELLATION_REASON_LABEL"] = clean["CANCELLATION_REASON"].map(reason_map).fillna("Not cancelled")
    clean["ROUTE"] = clean["ORIGIN_AIRPORT"].astype(str) + " → " + clean["DESTINATION_AIRPORT"].astype(str)
    return clean
