import requests
import csv
from datetime import datetime, timedelta
import xml.etree.ElementTree as ET
import os

API_KEY = os.getenv("TIMECAMP_API_KEY")
BASE_URL = "https://app.timecamp.com/third_party/api"

def fetch_time_entries(start_date, end_date):
    if not API_KEY:
        raise ValueError("TIMECAMP_API_KEY environment variable is not set")
    
    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }
    params = {
        "from": start_date.strftime("%Y-%m-%d"),
        "to": end_date.strftime("%Y-%m-%d"),
        "opt_fields": "breadcrumps"
    }
    response = requests.get(f"{BASE_URL}/entries", headers=headers, params=params)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
    response.raise_for_status()  # Raise an exception for HTTP errors
    xml_content = response.text
    # Save raw XML to file
    xml_dir = "raw_xml_data"
    os.makedirs(xml_dir, exist_ok=True)
    xml_filename = f"{start_date.strftime("%Y-%m")}.xml"
    with open(os.path.join(xml_dir, xml_filename), "w", encoding="utf-8") as f:
        f.write(xml_content)
    return ET.fromstring(xml_content)

def format_entries_for_csv(xml_root):
    formatted_data = []
    for item in xml_root.findall('item'):
        date_str = item.find('date').text
        date = datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
        
        duration_seconds = int(item.find('duration').text)
        hours = duration_seconds // 3600
        minutes = (duration_seconds % 3600) // 60
        time_str = f"{int(hours):02d}:{int(minutes):02d}"
        
        description = item.find('name').text
        
        breadcrumps = item.find('breadcrumps').text
        category = breadcrumps if breadcrumps else ""
        formatted_data.append({"Day": date, "Time": time_str, "Description": description, "Category": category})
    return formatted_data

def main():
    start_year = 2024
    start_month = 7
    end_year = 2025
    end_month = 6

    all_entries = []

    current_date = datetime(start_year, start_month, 1)
    while current_date.year < end_year or (current_date.year == end_year and current_date.month <= end_month):
        next_month = current_date.replace(day=28) + timedelta(days=4)  # Advance to next month
        end_of_month = next_month - timedelta(days=next_month.day)

        print(f"Fetching data for {current_date.strftime('%B %Y')}...")
        try:
            xml_root = fetch_time_entries(current_date, end_of_month)
            all_entries.extend(format_entries_for_csv(xml_root))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data for {current_date.strftime('%B %Y')}: {e}")
        
        current_date = end_of_month + timedelta(days=1)

    output_csv_file = "timecamp_entries.csv"
    with open(output_csv_file, "w", newline="", encoding="utf-8") as csvfile:
        fieldnames = ["Day", "Time", "Description", "Category"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_entries)
    print(f"Time entries saved to {output_csv_file}")

if __name__ == "__main__":
    main()