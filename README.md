# Data Cleaning & Reporting Automation

This project demonstrates an end-to-end data cleaning and reporting workflow in Python.

## Features
- Cleans missing values, duplicates, and inconsistent text/date fields
- Standardizes categories and converts data types
- Exports cleaned data to CSV and Excel
- Generates summary visualizations
- Creates an automated HTML report

## Setup

1. Create a virtual environment (optional but recommended)
2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Run the automation

```bash
python data_cleaning_report.py
```

## Output

The script generates:
- `data/cleaned/cleaned_data.csv`
- `data/cleaned/cleaned_data.xlsx`
- `reports/summary_report.html`
- `reports/region_sales.png`
- `reports/age_distribution.png`
- `reports/status_distribution.png`
- `reports/summary.json`

## Customization

You can point the pipeline at a different input file by editing the script or passing a custom path in code.
