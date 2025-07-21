# Timecamp Data Extractor and Billing Calculator

This project extracts time tracking data from Timecamp API and calculates billing statistics for consulting work.

## Description

The project consists of three main components:
1. **Data Extraction**: Fetches time entries from Timecamp API and converts them to CSV format
2. **Billing Analysis**: Analyzes the extracted data to calculate billable vs non-billable hours with detailed breakdowns
3. **Work From Home Extraction**: Filters and formats work from home entries for external applications

## Files

- `timecamp_extractor.py` - Extracts data from Timecamp API and saves to CSV
- `calculate_billed_percentage.py` - Analyzes billing data and generates comprehensive reports
- `extract_wfh_entries.py` - Extracts work from home entries in simplified format
- `timecamp_entries.csv` - Generated CSV file with all time entries
- `work_from_home_entries.csv` - Generated CSV file with work from home entries only
- `raw_xml_data/` - Raw XML responses from Timecamp API (for backup)

## Requirements

```
requests
```

Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### 1. Extract Data from Timecamp

```bash
python timecamp_extractor.py
```

This will:
- Fetch time entries from Timecamp API for the specified date range
- Save raw XML data to `raw_xml_data/` directory
- Generate `timecamp_entries.csv` with formatted data

### 2. Generate Billing Report

```bash
python calculate_billed_percentage.py
```

This will output:
- Total worked hours (excluding leave)
- Billable vs non-billable hour breakdown
- Client-project specific billing breakdown
- Location breakdown (work from home vs office)
- Percentage calculations against annual targets

### 3. Extract Work From Home Entries

```bash
python extract_wfh_entries.py
```

This will:
- Filter for work from home entries only
- Group by day and sum durations
- Generate `work_from_home_entries.csv` in simplified format (Day,Duration,Description)

## Sample Outputs

### Billing Report
```
Total worked hours: XXX.XX hours
Total billable hours: XXX.XX hours
Total non-billable hours: XXX.XX hours
Total leave hours: XXX.XX hours
Hours worked from home: XXX.XX hours
Hours worked from office: XXX.XX hours
Consulting non-billable hours: XXX.XX hours
Percentage of billed hours (out of total worked hours): XX.XX%
Percentage of billed hours (out of 1760 annual hours): XX.XX%

Client Breakdown:
  Client A - Project 1: XXX.Xh billable + XX.Xh non-billable = XXX.Xh total
  Client B - Project 2: XXX.Xh billable + XX.Xh non-billable = XXX.Xh total
  Client C - Project 3: XXX.Xh billable + XX.Xh non-billable = XXX.Xh total
  ...
```

### Work From Home CSV
```csv
Day,Duration,Description
01-01-2024,08:00,Work
02-01-2024,08:30,Work
03-01-2024,07:45,Work
...
```

## Configuration

### Environment Setup

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Timecamp API key:
   ```
   TIMECAMP_API_KEY=your_actual_api_key_here
   ```

### Date Range Configuration

Update the date range in `timecamp_extractor.py` if needed:

```python
start_year = 2024
start_month = 7
end_year = 2025
end_month = 6
```

## Features

- **Comprehensive billing analysis** with client-project breakdown
- **Accurate categorization** of billable, non-billable, and internal work
- **Location tracking** (work from home vs office)
- **Handles archived projects** correctly in client breakdown
- **Exports work from home data** in format suitable for external applications
- **Raw data backup** for audit and verification purposes