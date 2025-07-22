import csv
from datetime import datetime, timedelta
from collections import defaultdict

# Monthly workable hours configuration
MONTHLY_WORKABLE_HOURS = {
    1: 88,   # January
    2: 152,  # February  
    3: 160,  # March
    4: 144,  # April
    5: 168,  # May
    6: 160,  # June
    7: 160,  # July
    8: 160,  # August
    9: 160,  # September
    10: 160, # October
    11: 160, # November
    12: 88   # December
}

def parse_time_to_minutes(time_str):
    if ':' in time_str:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours * 60 + minutes
    else:
        # Handle cases where time might be in a different format or just hours
        return int(float(time_str)) * 60 # Assuming it's hours if no colon

def calculate_expected_workable_hours(start_date, end_date):
    """Calculate expected workable hours for a given date range"""
    if not start_date or not end_date:
        return 1760  # Default annual hours
    
    total_hours = 0
    current_date = start_date
    
    while current_date <= end_date:
        month = current_date.month
        year = current_date.year
        
        # Get the last day of the current month
        if month == 12:
            next_month = datetime(year + 1, 1, 1)
        else:
            next_month = datetime(year, month + 1, 1)
        
        month_end = next_month - timedelta(days=1)
        
        # Calculate what portion of the month is in our date range
        range_start = max(current_date, datetime(year, month, 1))
        range_end = min(end_date, month_end)
        
        if range_start <= range_end:
            days_in_month = (month_end - datetime(year, month, 1)).days + 1
            days_in_range = (range_end - range_start).days + 1
            
            month_workable_hours = MONTHLY_WORKABLE_HOURS.get(month, 160)
            proportional_hours = (days_in_range / days_in_month) * month_workable_hours
            total_hours += proportional_hours
        
        # Move to next month
        current_date = next_month
    
    return total_hours

def calculate_billed_percentage(file_path, start_date=None, end_date=None):
    expected_workable_hours = calculate_expected_workable_hours(start_date, end_date)
    expected_workable_minutes = expected_workable_hours * 60
    total_worked_minutes = 0
    billed_minutes = 0
    leave_minutes = 0
    wfh_minutes = 0
    office_minutes = 0
    consulting_non_billable_minutes = 0
    external_non_billable_minutes = 0
    
    # Client breakdown tracking
    client_breakdown = defaultdict(lambda: {'billable': 0, 'non_billable': 0})

    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # Parse date for filtering
            row_date = datetime.strptime(row['Day'], '%d-%m-%Y')
            
            # Skip rows outside date range if specified
            if start_date and row_date < start_date:
                continue
            if end_date and row_date > end_date:
                continue
                
            time_in_minutes = parse_time_to_minutes(row['Time'])
            category = row['Category']
            
            is_leave = "Leave" in row['Description']
            
            if is_leave:
                leave_minutes += time_in_minutes
            else:
                total_worked_minutes += time_in_minutes
                
                is_external_non_billable = "External" in category and "Non Billable" in category
                is_external_billable = "External" in category and "Billable" in category and not is_external_non_billable
                is_internal = "Internal" in category
                
                if is_external_non_billable:
                    external_non_billable_minutes += time_in_minutes
                    # Extract client and project name for breakdown
                    parts = category.split(' / ')
                    if len(parts) >= 3:
                        client_name = parts[2]  # Index 2 is the client
                        project_name = ""
                        
                        if len(parts) >= 4:
                            # Handle archived projects: skip "Archived" and use actual project name
                            if parts[3] == "Archived" and len(parts) >= 5:
                                project_name = parts[4]
                            else:
                                project_name = parts[3]
                        
                        # Create client-project key
                        if project_name:
                            client_project = f"{client_name} - {project_name}"
                        else:
                            client_project = client_name
                        
                        client_breakdown[client_project]['non_billable'] += time_in_minutes / 60
                elif is_external_billable:
                    billed_minutes += time_in_minutes
                    # Extract client and project name for breakdown
                    parts = category.split(' / ')
                    if len(parts) >= 3:
                        client_name = parts[2]  # Index 2 is the client
                        project_name = ""
                        
                        if len(parts) >= 4:
                            # Handle archived projects: skip "Archived" and use actual project name
                            if parts[3] == "Archived" and len(parts) >= 5:
                                project_name = parts[4]
                            else:
                                project_name = parts[3]
                        
                        # Create client-project key
                        if project_name:
                            client_project = f"{client_name} - {project_name}"
                        else:
                            client_project = client_name
                        
                        client_breakdown[client_project]['billable'] += time_in_minutes / 60
                elif is_internal:
                    consulting_non_billable_minutes += time_in_minutes

                if "Work From Home" in category:
                    wfh_minutes += time_in_minutes
                elif "FAIR office" in category or "Client office" in category:
                    office_minutes += time_in_minutes
    
    non_billable_minutes = external_non_billable_minutes
    percentage = (billed_minutes / expected_workable_minutes) * 100
    return percentage, total_worked_minutes, billed_minutes, non_billable_minutes, leave_minutes, wfh_minutes, office_minutes, consulting_non_billable_minutes, client_breakdown, expected_workable_hours

def print_utilization_report(period_name, billed_percentage, total_worked_minutes, billed_minutes, non_billable_minutes, leave_minutes, wfh_minutes, office_minutes, consulting_non_billable_minutes, client_breakdown, expected_workable_hours):
    # Professional color palette
    DARK_BLUE = '\033[34m'    # Professional blue
    DARK_GREEN = '\033[32m'   # Success green
    ORANGE = '\033[33m'       # Warning/info orange
    DARK_RED = '\033[31m'     # Error/leave red
    PURPLE = '\033[35m'       # Accent purple
    DARK_CYAN = '\033[36m'    # Information cyan
    GRAY = '\033[90m'         # Subtle gray
    BOLD = '\033[1m'
    END = '\033[0m'
    
    # Determine performance color and icon
    if billed_percentage >= 70:
        perf_color = DARK_GREEN
        perf_icon = "●"
    elif billed_percentage >= 60:
        perf_color = ORANGE
        perf_icon = "●"
    else:
        perf_color = DARK_RED
        perf_icon = "●"
    
    print(f"\n{BOLD}{DARK_BLUE}{'▬' * 65}{END}")
    print(f"{BOLD}{DARK_BLUE}║{END} {BOLD}{period_name.upper()}{END} {BOLD}{DARK_BLUE}║{END}")
    print(f"{BOLD}{DARK_BLUE}{'▬' * 65}{END}")
    
    total_worked_hours = total_worked_minutes / 60
    print(f"{GRAY}Expected Workable Hours:{END} {BOLD}{expected_workable_hours:.2f}{END} hrs")
    print(f"{DARK_CYAN}Total Worked Hours:{END} {BOLD}{total_worked_hours:.2f}{END} hrs")
    print(f"{DARK_GREEN}Billable Hours:{END} {BOLD}{billed_minutes / 60:.2f}{END} hrs")
    print(f"{ORANGE}Non-Billable Hours:{END} {BOLD}{non_billable_minutes / 60:.2f}{END} hrs")
    print(f"{DARK_RED}Leave Hours:{END} {BOLD}{leave_minutes / 60:.2f}{END} hrs")
    print(f"{PURPLE}Remote Work:{END} {BOLD}{wfh_minutes / 60:.2f}{END} hrs")
    print(f"{DARK_CYAN}Office Work:{END} {BOLD}{office_minutes / 60:.2f}{END} hrs")
    print(f"{ORANGE}Internal Hours:{END} {BOLD}{consulting_non_billable_minutes / 60:.2f}{END} hrs")
    print(f"{perf_color}Utilization Rate:{END} {perf_color}{BOLD}{billed_percentage:.2f}%{END} {perf_color}{perf_icon}{END}")
    
    # Client breakdown
    if client_breakdown:
        print(f"\n{BOLD}{DARK_BLUE}CLIENT PORTFOLIO{END}")
        print(f"{GRAY}{'─' * 50}{END}")
        for client, hours in sorted(client_breakdown.items()):
            total_client = hours['billable'] + hours['non_billable']
            print(f"  {BOLD}{client}{END}")
            print(f"    {DARK_GREEN}Billable:{END} {hours['billable']:.1f}h {GRAY}|{END} {ORANGE}Non-Billable:{END} {hours['non_billable']:.1f}h {GRAY}|{END} {BOLD}Total:{END} {total_client:.1f}h")
    
    # Verification
    calculated_total = billed_minutes + non_billable_minutes + consulting_non_billable_minutes
    print(f"\n{BOLD}{GRAY}VERIFICATION{END}")
    print(f"{GRAY}Total Hours:{END} {billed_minutes/60:.2f} + {non_billable_minutes/60:.2f} + {consulting_non_billable_minutes/60:.2f} = {BOLD}{calculated_total/60:.2f}{END} hrs")

if __name__ == "__main__":
    csv_file_path = "timecamp_entries.csv"
    
    # Financial year calculation (July 2024 to June 2025)
    
    # Annual calculation (full financial year)
    annual_start = datetime(2024, 7, 1)
    annual_end = datetime(2025, 6, 30)
    
    annual_results = calculate_billed_percentage(csv_file_path, annual_start, annual_end)
    print_utilization_report("ANNUAL (Jul 2024 - Jun 2025)", *annual_results)
    
    # First half (Jul-Dec 2024)
    h1_start = datetime(2024, 7, 1)
    h1_end = datetime(2024, 12, 31)
    
    h1_results = calculate_billed_percentage(csv_file_path, h1_start, h1_end)
    print_utilization_report("FIRST HALF (Jul-Dec 2024)", *h1_results)
    
    # Second half (Jan-Jun 2025)
    h2_start = datetime(2025, 1, 1)
    h2_end = datetime(2025, 6, 30)
    
    h2_results = calculate_billed_percentage(csv_file_path, h2_start, h2_end)
    print_utilization_report("SECOND HALF (Jan-Jun 2025)", *h2_results)
