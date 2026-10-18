import requests
import pandas as pd
import os

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(DATA_DIR, "openphish.csv")

def download_openphish_dataset() -> str:
    """Download the free OpenPhish feed (plain‑text URL list) and save as CSV."""
    url = "https://openphish.com/feed.txt"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    lines = [line.strip() for line in resp.text.splitlines() if line.strip()]
    df = pd.DataFrame(lines, columns=["url"])
    df.to_csv(CSV_PATH, index=False)
    print(f"OpenPhish dataset saved to {CSV_PATH}")
    return CSV_PATH
