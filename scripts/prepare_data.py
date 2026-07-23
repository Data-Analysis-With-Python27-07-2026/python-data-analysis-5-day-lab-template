from __future__ import annotations

import argparse
import csv
import io
import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests

FIGSHARE_URL = "https://figshare.com/ndownloader/files/17614757"
EXPECTED_COLUMNS = {
    "YEAR", "MONTH", "DAY", "DAY_OF_WEEK", "AIRLINE", "FLIGHT_NUMBER",
    "ORIGIN_AIRPORT", "DESTINATION_AIRPORT", "SCHEDULED_DEPARTURE",
    "DEPARTURE_DELAY", "SCHEDULED_TIME", "DISTANCE", "ARRIVAL_DELAY",
    "DIVERTED", "CANCELLED", "CANCELLATION_REASON", "WEATHER_DELAY",
}


def generate_fallback(rows: int, seed: int = 20260727) -> pd.DataFrame:
    """Create a deterministic schema-compatible dataset only when explicitly requested."""
    rng = np.random.default_rng(seed)
    airlines = np.array(["AA", "AS", "B6", "DL", "EV", "F9", "HA", "MQ", "NK", "OO", "UA", "US", "VX", "WN"])
    airports = np.array(["ATL", "LAX", "ORD", "DFW", "JFK", "DEN", "SFO", "SEA", "LAS", "MCO", "CLT", "PHX", "IAH", "MIA", "BOS", "MSP", "DTW", "PHL", "LGA", "BWI"])

    month = rng.integers(1, 13, rows)
    day = rng.integers(1, 29, rows)
    date = pd.to_datetime({"year": np.full(rows, 2015), "month": month, "day": day})
    day_of_week = date.dt.dayofweek.to_numpy() + 1
    airline = rng.choice(airlines, rows)
    origin = rng.choice(airports, rows)
    destination = rng.choice(airports, rows)
    same = origin == destination
    while same.any():
        destination[same] = rng.choice(airports, same.sum())
        same = origin == destination

    scheduled_hour = rng.integers(5, 23, rows)
    scheduled_minute = rng.choice(np.arange(0, 60, 5), rows)
    scheduled_departure = scheduled_hour * 100 + scheduled_minute
    distance = np.clip(rng.gamma(2.4, 380, rows) + 100, 80, 3000).round().astype(int)
    scheduled_time = np.clip(distance / 7.2 + rng.normal(35, 12, rows), 45, 420).round()
    congestion = np.where((scheduled_hour >= 16) & (scheduled_hour <= 20), 8, 0)
    seasonal = np.where(np.isin(month, [1, 2, 6, 7, 8, 12]), 5, 0)
    departure_delay = np.round(rng.normal(-2 + congestion + seasonal, 16, rows) + rng.exponential(25, rows) * (rng.random(rows) < .15), 1)
    cancelled = (rng.random(rows) < .015).astype(int)
    diverted = ((rng.random(rows) < .003) & (cancelled == 0)).astype(int)
    arrival_delay = np.round(departure_delay * .72 + rng.normal(0, 12, rows), 1)
    taxi_out = np.clip(rng.normal(16, 5, rows), 4, 65).round(1)
    air_time = np.clip(scheduled_time - taxi_out - rng.normal(9, 3, rows), 20, None).round(1)
    elapsed_time = (air_time + taxi_out + np.clip(rng.normal(8, 3, rows), 2, 30)).round(1)

    missing_on_cancel = [departure_delay, arrival_delay, taxi_out, air_time, elapsed_time]
    for values in missing_on_cancel:
        values[cancelled == 1] = np.nan

    cancellation_reason = np.full(rows, None, dtype=object)
    cancellation_reason[cancelled == 1] = rng.choice(np.array(["A", "B", "C", "D"]), cancelled.sum())
    delay_positive = np.clip(departure_delay, 0, None)
    component = lambda fraction: np.where(delay_positive > 15, delay_positive * rng.uniform(*fraction, rows), np.nan)

    df = pd.DataFrame({
        "YEAR": 2015, "MONTH": month, "DAY": day, "DAY_OF_WEEK": day_of_week,
        "AIRLINE": airline, "FLIGHT_NUMBER": rng.integers(1, 9999, rows),
        "TAIL_NUMBER": [f"N{x:05d}" for x in rng.integers(1, 99999, rows)],
        "ORIGIN_AIRPORT": origin, "DESTINATION_AIRPORT": destination,
        "SCHEDULED_DEPARTURE": scheduled_departure, "DEPARTURE_TIME": np.where(cancelled, np.nan, scheduled_departure),
        "DEPARTURE_DELAY": departure_delay, "TAXI_OUT": taxi_out, "WHEELS_OFF": np.nan,
        "SCHEDULED_TIME": scheduled_time, "ELAPSED_TIME": elapsed_time, "AIR_TIME": air_time,
        "DISTANCE": distance, "WHEELS_ON": np.nan, "TAXI_IN": np.clip(rng.normal(8, 3, rows), 2, 35).round(1),
        "SCHEDULED_ARRIVAL": np.nan, "ARRIVAL_TIME": np.nan, "ARRIVAL_DELAY": arrival_delay,
        "DIVERTED": diverted, "CANCELLED": cancelled, "CANCELLATION_REASON": cancellation_reason,
        "AIR_SYSTEM_DELAY": component((.10, .40)), "SECURITY_DELAY": component((0, .02)),
        "AIRLINE_DELAY": component((.15, .50)), "LATE_AIRCRAFT_DELAY": component((.10, .45)),
        "WEATHER_DELAY": component((.05, .35)),
    })
    duplicate_n = max(5, rows // 2000)
    return pd.concat([df, df.iloc[:duplicate_n]], ignore_index=True)


def stream_figshare(rows: int) -> pd.DataFrame:
    """Stream the requested number of rows from the official Figshare file."""
    headers = {"User-Agent": "Mozilla/5.0 PythonDataAnalysisTraining/1.0"}
    with requests.get(FIGSHARE_URL, stream=True, timeout=(30, 180), headers=headers) as response:
        response.raise_for_status()
        response.raw.decode_content = True
        wrapper = io.TextIOWrapper(response.raw, encoding="utf-8-sig", newline="")
        reader = csv.reader(wrapper)
        header = next(reader)
        records = []
        for row in reader:
            records.append(row)
            if len(records) >= rows:
                break
    df = pd.DataFrame(records, columns=header)
    for col in df.columns:
        if col not in {"AIRLINE", "TAIL_NUMBER", "ORIGIN_AIRPORT", "DESTINATION_AIRPORT", "CANCELLATION_REASON"}:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    missing = EXPECTED_COLUMNS.difference(df.columns)
    if missing:
        raise ValueError(f"Downloaded data is missing expected columns: {sorted(missing)}")
    return df


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify or regenerate the flights training sample.")
    parser.add_argument("--rows", type=int, default=50000)
    parser.add_argument("--force", action="store_true", help="Replace the bundled subset from the official remote file.")
    parser.add_argument("--allow-fallback", action="store_true", help="Generate deterministic substitute data if remote download fails.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    data_dir.mkdir(exist_ok=True)
    output = data_dir / "flights_sample.csv"
    metadata_path = data_dir / "DATA_SOURCE.json"

    if output.exists() and not args.force:
        df = pd.read_csv(output, nrows=5)
        missing = EXPECTED_COLUMNS.difference(df.columns)
        if missing:
            raise ValueError(f"Bundled data is missing expected columns: {sorted(missing)}")
        print(f"Training data ready: {output}")
        return

    source = "figshare_stream"
    note = "Rows streamed directly from the official Figshare flights.csv file."
    try:
        df = stream_figshare(args.rows)
    except Exception as exc:
        if not args.allow_fallback:
            raise RuntimeError("Remote download failed. Re-run with --allow-fallback or restore the bundled data file.") from exc
        source = "synthetic_fallback"
        note = f"Remote download failed; deterministic schema-compatible fallback generated: {type(exc).__name__}: {exc}"
        df = generate_fallback(args.rows)

    df.to_csv(output, index=False)
    metadata = {
        "source": source,
        "rows": int(len(df)),
        "columns": int(len(df.columns)),
        "figshare_article": "https://figshare.com/articles/dataset/flights_csv/9820139",
        "figshare_file_id": 17614757,
        "note": note,
    }
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Created {output} with shape {df.shape}; source={source}")


if __name__ == "__main__":
    main()
