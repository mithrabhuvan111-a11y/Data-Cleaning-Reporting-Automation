import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


INPUT_PATH = Path("data/raw/sample_data.csv")
OUTPUT_DIR = Path("data/cleaned")
REPORT_DIR = Path("reports")


def load_data(input_path: Path) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    original_shape = df.shape
    df = df.copy()

    # Normalize column names and trim whitespace
    df.columns = [str(col).strip().lower() for col in df.columns]
    df = df.apply(lambda col: col.astype(str).str.strip() if col.dtype == object else col)

    # Remove exact duplicates
    before_duplicates = df.shape[0]
    df = df.drop_duplicates()
    duplicates_removed = before_duplicates - df.shape[0]

    # Standardize text fields
    text_cols = ["name", "region", "status"]
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].replace({"": pd.NA}).fillna("Unknown")
            df[col] = df[col].astype(str).str.strip()
            if col == "region":
                df[col] = df[col].str.lower().str.replace(r"\s+", " ", regex=True)
                df[col] = df[col].map(
                    {
                        "north": "North",
                        "south": "South",
                        "east": "East",
                        "west": "West",
                        "central": "Central",
                        "n": "North",
                        "s": "South",
                        "e": "East",
                        "w": "West",
                    }
                ).fillna(df[col].str.title())
            elif col == "status":
                df[col] = df[col].str.lower().map(
                    {
                        "active": "Active",
                        "inactive": "Inactive",
                        "pending": "Pending",
                    }
                ).fillna("Unknown")

    # Missing value handling
    numeric_cols = ["age", "sales"]
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            median = df[col].median()
            df[col] = df[col].fillna(median)

    # Parse date
    if "signup_date" in df.columns:
        df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
        df["signup_date"] = df["signup_date"].fillna(pd.Timestamp("1970-01-01"))

    # Fill remaining missing strings
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].fillna("Unknown")

    clean_stats = {
        "original_shape": original_shape,
        "cleaned_shape": df.shape,
        "duplicates_removed": duplicates_removed,
        "missing_before": int(df.isna().sum().sum()),
        "missing_after": int(df.isna().sum().sum()),
    }
    df.attrs["clean_stats"] = clean_stats
    return df


def create_visuals(df: pd.DataFrame) -> None:
    REPORT_DIR.mkdir(exist_ok=True)

    sns.set(style="whitegrid")

    # Region sales
    region_sales = df.groupby("region")["sales"].mean().sort_values(ascending=False)
    plt.figure(figsize=(7, 4))
    region_sales.plot(kind="bar", color="teal")
    plt.title("Average Sales by Region")
    plt.ylabel("Average Sales")
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "region_sales.png", dpi=150)
    plt.close()

    # Age distribution
    plt.figure(figsize=(7, 4))
    sns.histplot(df["age"], bins=8, kde=True, color="steelblue")
    plt.title("Age Distribution")
    plt.xlabel("Age")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "age_distribution.png", dpi=150)
    plt.close()

    # Status counts
    status_counts = df["status"].value_counts()
    plt.figure(figsize=(6, 4))
    status_counts.plot(kind="pie", autopct="%1.1f%%", colors=["#4C72B0", "#55A868", "#C44E52"])
    plt.title("Customer Status Distribution")
    plt.ylabel("")
    plt.tight_layout()
    plt.savefig(REPORT_DIR / "status_distribution.png", dpi=150)
    plt.close()


def create_report(df: pd.DataFrame) -> None:
    REPORT_DIR.mkdir(exist_ok=True)
    stats = df.attrs["clean_stats"]

    missing_summary = df.isna().sum().sort_values(ascending=False)
    numeric_summary = df[["age", "sales"]].describe().to_string()
    region_summary = df.groupby("region").size().to_dict()
    status_summary = df["status"].value_counts().to_dict()

    html = f"""
    <html>
      <head>
        <title>Data Cleaning & Reporting Automation</title>
        <style>
          body {{ font-family: Arial, sans-serif; margin: 2rem; color: #1f2937; }}
          h1, h2 {{ color: #0f172a; }}
          .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1rem; }}
          .card {{ background: #f8fafc; border: 1px solid #cbd5e1; border-radius: 8px; padding: 1rem; }}
          pre {{ background: #0f172a; color: #e2e8f0; padding: 1rem; border-radius: 8px; overflow-x: auto; }}
        </style>
      </head>
      <body>
        <h1>Data Cleaning & Reporting Automation</h1>
        <p>Automated workflow completed successfully.</p>

        <div class="grid">
          <div class="card">
            <h2>Data Quality Summary</h2>
            <p><strong>Original rows:</strong> {stats['original_shape'][0]}</p>
            <p><strong>Cleaned rows:</strong> {stats['cleaned_shape'][0]}</p>
            <p><strong>Duplicates removed:</strong> {stats['duplicates_removed']}</p>
            <p><strong>Missing values after cleaning:</strong> {stats['missing_after']}</p>
          </div>

          <div class="card">
            <h2>Region Distribution</h2>
            <pre>{region_summary}</pre>
          </div>

          <div class="card">
            <h2>Status Distribution</h2>
            <pre>{status_summary}</pre>
          </div>
        </div>

        <h2>Numeric Summary</h2>
        <pre>{numeric_summary}</pre>

        <h2>Missing Values</h2>
        <pre>{missing_summary.to_string()}</pre>

        <h2>Visual Outputs</h2>
        <ul>
          <li><a href="region_sales.png">Average Sales by Region</a></li>
          <li><a href="age_distribution.png">Age Distribution</a></li>
          <li><a href="status_distribution.png">Customer Status Distribution</a></li>
        </ul>
      </body>
    </html>
    """

    (REPORT_DIR / "summary_report.html").write_text(html, encoding="utf-8")


def export_outputs(df: pd.DataFrame) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    cleaned_csv = OUTPUT_DIR / "cleaned_data.csv"
    cleaned_xlsx = OUTPUT_DIR / "cleaned_data.xlsx"

    df.to_csv(cleaned_csv, index=False)
    df.to_excel(cleaned_xlsx, index=False)

    summary = {
        "rows": int(df.shape[0]),
        "columns": list(df.columns),
        "missing_values": int(df.isna().sum().sum()),
        "average_sales": float(df["sales"].mean()),
        "average_age": float(df["age"].mean()),
    }

    (REPORT_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    df = load_data(INPUT_PATH)
    cleaned_df = clean_data(df)
    create_visuals(cleaned_df)
    create_report(cleaned_df)
    export_outputs(cleaned_df)
    print("Data cleaning and reporting workflow completed.")
    print(f"Generated outputs in {OUTPUT_DIR} and {REPORT_DIR}")


if __name__ == "__main__":
    main()
