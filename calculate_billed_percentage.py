import csv
from datetime import timedelta
from collections import defaultdict

def parse_time_to_minutes(time_str):
    if ':' in time_str:
        parts = time_str.split(':')
        hours = int(parts[0])
        minutes = int(parts[1])
        return hours * 60 + minutes
    else:
        # Handle cases where time might be in a different format or just hours
        return int(float(time_str)) * 60 # Assuming it's hours if no colon

def calculate_billed_percentage(file_path):
    total_annual_hours = 1760
    total_annual_minutes = total_annual_hours * 60
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
    percentage = (billed_minutes / total_annual_minutes) * 100
    return percentage, total_worked_minutes, billed_minutes, non_billable_minutes, leave_minutes, wfh_minutes, office_minutes, consulting_non_billable_minutes, client_breakdown

if __name__ == "__main__":
    csv_file_path = "timecamp_entries.csv"
    billed_percentage, total_worked_minutes, billed_minutes, non_billable_minutes, leave_minutes, wfh_minutes, office_minutes, consulting_non_billable_minutes, client_breakdown = calculate_billed_percentage(csv_file_path)
    
    total_worked_hours = total_worked_minutes / 60
    print(f"Total worked hours: {total_worked_hours:.2f}")
    print(f"Total worked hours: {total_worked_minutes / 60:.2f} hours")
    print(f"Total billable hours: {billed_minutes / 60:.2f} hours")
    print(f"Total non-billable hours: {non_billable_minutes / 60:.2f} hours")
    print(f"Total leave hours: {leave_minutes / 60:.2f} hours")
    print(f"Hours worked from home: {wfh_minutes / 60:.2f} hours")
    print(f"Hours worked from office: {office_minutes / 60:.2f} hours")
    print(f"Consulting non-billable hours: {consulting_non_billable_minutes / 60:.2f} hours")
    print(f"Percentage of billed hours (out of total worked hours): {(billed_minutes / total_worked_minutes) * 100:.2f}%")
    print(f"Percentage of billed hours (out of 1760 annual hours): {billed_percentage:.2f}%")
    
    # Client breakdown
    print(f"\nClient Breakdown:")
    for client, hours in sorted(client_breakdown.items()):
        total_client = hours['billable'] + hours['non_billable']
        print(f"  {client}: {hours['billable']:.1f}h billable + {hours['non_billable']:.1f}h non-billable = {total_client:.1f}h total")
    
    # Verification
    calculated_total = billed_minutes + non_billable_minutes + consulting_non_billable_minutes
    print(f"\nVerification: {billed_minutes/60:.2f} + {non_billable_minutes/60:.2f} + {consulting_non_billable_minutes/60:.2f} = {calculated_total/60:.2f} (should equal {total_worked_minutes/60:.2f})")
