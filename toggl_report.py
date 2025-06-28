import os
import json
import sys
from datetime import datetime, timedelta, timezone
import urllib.request
import base64

# --- Configuration ---
TOKEN_FILE_PATH = "./.toggl_token"
DAYS_TO_REPORT = 7
# Tags that should be detailed by project name
DETAIL_TAGS = {
    "consume-video": "Entertainment",
    "input-book": "Reading"
}

def get_api_token():
    """Reads the Toggl API token from the specified file."""
    expanded_path = os.path.expanduser(TOKEN_FILE_PATH)
    if not os.path.exists(expanded_path):
        print(f"Error: Token file not found at {expanded_path}")
        return None
    with open(expanded_path, 'r') as f:
        return f.read().strip()

def make_api_request(url, token):
    """Makes an authenticated request to the Toggl API."""
    auth_header = base64.b64encode(f"{token}:api_token".encode()).decode()
    headers = {"Authorization": f"Basic {auth_header}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            if response.status == 200:
                return json.loads(response.read().decode())
            else:
                print(f"Error fetching data from {url}: {response.status} {response.reason}")
                return None
    except urllib.error.URLError as e:
        print(f"Error: Failed to connect to Toggl API. {e.reason}")
        return None

def fetch_time_entries(token, start_date, end_date):
    """Fetches time entries for a given date range."""
    start_iso = start_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_iso = end_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    url = f"https://api.track.toggl.com/api/v9/me/time_entries?start_date={start_iso}&end_date={end_iso}"
    return make_api_request(url, token)

def fetch_projects(token, workspace_id):
    """Fetches all projects for a given workspace."""
    url = f"https://api.track.toggl.com/api/v9/workspaces/{workspace_id}/projects"
    projects = make_api_request(url, token)
    return {p['id']: p['name'] for p in projects} if projects else {}

def process_data(entries, projects_map):
    """Processes raw entries and projects into a structured report dictionary."""
    tag_durations = {}
    total_duration = 0
    detailed_items = {tag: set() for tag in DETAIL_TAGS}

    for entry in entries:
        duration = entry.get("duration", 0)
        if duration < 0:
            start_time = datetime.fromisoformat(entry["start"])
            duration = (datetime.now(timezone.utc) - start_time).total_seconds()
        
        total_duration += duration
        tags = entry.get("tags", ["Untagged"])

        for tag in tags:
            tag_durations[tag] = tag_durations.get(tag, 0) + duration
            if tag in detailed_items and entry.get('project_id'):
                project_name = projects_map.get(entry['project_id'])
                if project_name:
                    detailed_items[tag].add(project_name)
    
    return {
        "total_hours": total_duration / 3600,
        "tag_durations": tag_durations,
        "detailed_items": detailed_items,
        "total_duration_seconds": total_duration
    }

def print_terminal_report(data):
    """Prints a summary report to the terminal."""
    print("--- Toggl Weekly Time Report ---")
    print(f"\nTotal time tracked: {data['total_hours']:.2f} hours\n")
    print("Breakdown by Tag:")
    print("-" * 40)
    
    sorted_tags = sorted(data['tag_durations'].items(), key=lambda item: item[1], reverse=True)
    
    for tag, duration in sorted_tags:
        hours = duration / 3600
        percentage = (duration / data['total_duration_seconds']) * 100 if data['total_duration_seconds'] > 0 else 0
        print(f"- {tag:<20} | {hours:>5.2f} hours ({percentage:.1f}%)")
    
    print("-" * 40)

    for tag, section_title in DETAIL_TAGS.items():
        if data['detailed_items'].get(tag):
            print(f"\n{section_title}:")
            for item in sorted(list(data['detailed_items'][tag])):
                print(f"- {item}")
    print("\n")


def write_weekly_post(data):
    """Generates and writes the weekly blog post."""
    latest_week = 0
    post_dir = "/Users/joeytat/Documents/playground/blog/content/posts/"
    for fname in os.listdir(post_dir):
        if fname.startswith("2025_week") and fname.endswith(".md"):
            try:
                week_num = int(fname.split("week")[1].split(".")[0])
                if week_num > latest_week:
                    latest_week = week_num
            except (ValueError, IndexError):
                continue
    
    new_week_num = latest_week + 1
    file_path = os.path.join(post_dir, f"2025_week{new_week_num}.md")
    
    # --- Build Post Content ---
    title = f"2025 week {new_week_num}: 用数据复盘一周"
    date = datetime.now().strftime("%Y-%m-%d")
    
    content = f"""+++
title = "{title}"
date = "{date}"
tags = ["周记"]
+++

本周总共记录了 **{data['total_hours']:.2f} 小时**。

### 工作与输出

"""
    
    # Add tag breakdown
    sorted_tags = sorted(data['tag_durations'].items(), key=lambda item: item[1], reverse=True)
    for tag, duration in sorted_tags:
        hours = duration / 3600
        percentage = (duration / data['total_duration_seconds']) * 100 if data['total_duration_seconds'] > 0 else 0
        content += f"- **{tag}:** {hours:.2f} 小时 ({percentage:.1f}%)\n"

    # Add detailed sections
    for tag, section_title in DETAIL_TAGS.items():
        items = data['detailed_items'].get(tag)
        if items:
            content += f"\n### {section_title}\n\n"
            for item in sorted(list(items)):
                content += f"- 《{item}》 ⭐️⭐️⭐️⭐️⭐️\n  \n"

    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Successfully created weekly post: {file_path}")
    except IOError as e:
        print(f"Error writing file: {e}")


def main():
    """Main function to run the report generation."""
    token = get_api_token()
    if not token:
        return

    # --- Date Range Calculation ---
    # Default: last 7 days
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=DAYS_TO_REPORT)

    if len(sys.argv) == 2: # Handle weeks_ago
        try:
            weeks_ago = int(sys.argv[1])
            end_date = datetime.now(timezone.utc) - timedelta(weeks=weeks_ago)
            start_date = end_date - timedelta(days=DAYS_TO_REPORT)
        except ValueError:
            print("Error: Invalid argument. Expected an integer for weeks_ago.")
            return
    elif len(sys.argv) == 3: # Handle specific date range
        try:
            start_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').replace(tzinfo=timezone.utc)
            # Add 1 day to end_date to make the range inclusive
            end_date = datetime.strptime(sys.argv[2], '%Y-%m-%d').replace(tzinfo=timezone.utc) + timedelta(days=1)
        except ValueError:
            print("Error: Invalid date format. Use YYYY-MM-DD YYYY-MM-DD.")
            return
    
    print(f"Fetching Toggl data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}...")
    
    entries = fetch_time_entries(token, start_date, end_date)
    if not entries:
        print("No time entries found for the specified period.")
        return

    workspace_id = entries[0].get('workspace_id')
    if not workspace_id:
        print("Could not determine workspace_id from time entries.")
        return
        
    projects_map = fetch_projects(token, workspace_id)
    
    report_data = process_data(entries, projects_map)
    
    print_terminal_report(report_data)
    write_weekly_post(report_data)

if __name__ == "__main__":
    main()