import csv
from collections import defaultdict

def parse_time_to_minutes(time_str):
    """Convert HH:MM format to minutes"""
    if ':' in time_str:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours * 60 + minutes
    else:
        return int(float(time_str)) * 60

def minutes_to_duration(minutes):
    """Convert minutes back to HH:MM format"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def extract_wfh_entries(input_file, output_file):
    """Extract work from home entries and group by day"""
    
    # Dictionary to store total minutes per day
    daily_totals = defaultdict(int)
    
    with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            category = row['Category']
            description = row['Description']
            
            # Skip leave entries
            if "Leave" in description:
                continue
            
            # Only include work from home entries
            if "Work From Home" in category:
                day = row['Day']
                time_in_minutes = parse_time_to_minutes(row['Time'])
                daily_totals[day] += time_in_minutes
    
    # Write output CSV
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['Day', 'Duration', 'Description']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Sort by date and write entries
        for day in sorted(daily_totals.keys()):
            total_minutes = daily_totals[day]
            duration = minutes_to_duration(total_minutes)
            
            writer.writerow({
                'Day': day,
                'Duration': duration,
                'Description': 'Work'
            })
    
    # Print summary
    total_days = len(daily_totals)
    total_hours = sum(daily_totals.values()) / 60
    
    print(f"Work From Home Summary:")
    print(f"Total days worked from home: {total_days}")
    print(f"Total work from home hours: {total_hours:.2f}")
    print(f"Average hours per WFH day: {total_hours/total_days:.2f}")
    print(f"Output saved to: {output_file}")

if __name__ == "__main__":
    input_file = "timecamp_entries.csv"
    output_file = "work_from_home_entries.csv"
    
    extract_wfh_entries(input_file, output_file)