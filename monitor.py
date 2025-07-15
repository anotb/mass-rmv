import json
import os
import sys
import time
import requests
from datetime import datetime
from dotenv import load_dotenv
from rmv_checker import get_rmv_data, setup_env_file

load_dotenv()

STATE_FILE = 'state.json'

def load_json(file_path):
    """Loads data from a JSON file."""
    if not os.path.exists(file_path):
        return {}
    with open(file_path, 'r') as f:
        return json.load(f)

def save_json(data, file_path):
    """Saves data to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def send_ntfy_notification(url, message):
    """Sends a notification to a ntfy URL."""
    try:
        requests.post(url, data=message.encode('utf-8'))
        print(f"Sent notification: {message}")
    except Exception as e:
        print(f"Error sending ntfy notification: {e}", file=sys.stderr)

def parse_date(date_str):
    """Parses the scraped date string into a datetime object."""
    if "No Appointments" in date_str or "No Date Found" in date_str:
        return None
    try:
        clean_date_str = date_str.strip().rstrip(',')
        return datetime.strptime(clean_date_str, '%a %b %d, %Y, %I:%M %p')
    except ValueError:
        try:
            return datetime.strptime(clean_date_str, '%a %b %d, %Y')
        except ValueError as e:
            print(f"Error parsing date string '{date_str}': {e}", file=sys.stderr)
            return None

def check_for_appointments(rmv_url, ntfy_url, locations_to_monitor, state):
    """The core logic for checking appointments and sending notifications."""
    print(f"--- Running RMV Appointment Check [{datetime.now()}] ---")
    
    live_data = get_rmv_data(rmv_url, locations_to_monitor)
    if not live_data:
        print("Could not fetch live appointment data.", file=sys.stderr)
        return state

    for location_data in live_data:
        location_id = str(location_data['id'])
        location_name = location_data['service_center']
        new_date_str = location_data['earliest_date']
        new_date = parse_date(new_date_str)

        if not new_date:
            print(f"No appointments found for {location_name}.")
            continue

        last_known_date_str = state.get(location_id)
        last_known_date = parse_date(last_known_date_str) if last_known_date_str else None

        if not last_known_date or new_date < last_known_date:
            # Check if the original scraped string contained a time component (AM/PM)
            if "AM" in new_date_str or "PM" in new_date_str:
                # We have a specific time
                message = f"New appointment at {location_name}: {new_date.strftime('%a, %b %d, %Y at %I:%M %p')}"
                state[location_id] = new_date.strftime('%a %b %d, %Y, %I:%M %p')
            else:
                # We only have a date
                message = f"New earliest date at {location_name}: {new_date.strftime('%a, %b %d, %Y')}"
                state[location_id] = new_date.strftime('%a %b %d, %Y')
            
            send_ntfy_notification(ntfy_url, message)
        else:
            print(f"No change for {location_name}. Earliest is still {last_known_date_str}")
    
    save_json(state, STATE_FILE)
    print("--- Check complete ---")
    return state

def run_monitor():
    """Main monitoring loop."""
    if not os.path.exists('.env'):
        print("Configuration file (.env) not found. Starting interactive setup...")
        setup_env_file()
        load_dotenv() # Reload environment variables after setup

    rmv_url = os.getenv("RMV_URL")
    ntfy_url = os.getenv("NTFY_URL")
    locations_to_monitor_ids = os.getenv("LOCATIONS_TO_MONITOR", "").split(',')

    if not all([rmv_url, ntfy_url, locations_to_monitor_ids]):
        print("Configuration is incomplete. Please run 'python3 rmv_checker.py' to set up.", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(STATE_FILE):
        reset_choice = input("Do you want to delete the existing state.json file? [y/N]: ").lower()
        if reset_choice == 'y':
            os.remove(STATE_FILE)
            print("Deleted state.json")
    
    state = load_json(STATE_FILE)

    try:
        frequency_minutes = int(input("How often to check for appointments (in minutes)? [default: 5]: ") or "5")
    except ValueError:
        frequency_minutes = 5

    print(f"Starting monitor. Will check every {frequency_minutes} minutes.")

    while True:
        try:
            # This is a simplified approach. A more robust solution would fetch all locations
            # and filter them by the IDs on each run to ensure the names are up to date.
            # For now, we pass the IDs and the scraper will have to handle it.
            # The current `get_rmv_data` expects a list of dicts, so we create it here.
            locations_to_monitor = [{'id': loc_id, 'service_center': f'ID-{loc_id}'} for loc_id in locations_to_monitor_ids]

            state = check_for_appointments(rmv_url, ntfy_url, locations_to_monitor, state)
        except Exception as e:
            print(f"An unexpected error occurred during the check: {e}", file=sys.stderr)
            print("The monitor will continue running.", file=sys.stderr)
        
        print(f"Sleeping for {frequency_minutes} minutes...")
        time.sleep(frequency_minutes * 60)

if __name__ == "__main__":
    run_monitor()

