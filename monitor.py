import sys

# --- Dependency Check ---
try:
    import requests
    from selenium import webdriver
    from dotenv import load_dotenv
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError as e:
    missing_module = str(e).split("'\")[1]
    print(f"FATAL: Missing required Python package '{missing_module}'.", file=sys.stderr)
    print("Please install all required packages by running the following command:", file=sys.stderr)
    print("\n    pip install -r requirements.txt\n", file=sys.stderr)
    sys.exit(1)

import json
import os
import time
import logging
from datetime import datetime
from rmv_checker import (
    get_rmv_data, 
    get_all_locations,
    prompt_for_rmv_url,
    prompt_for_ntfy_url,
    prompt_for_locations,
    prompt_for_frequency
)
from selenium.webdriver.chrome.service import Service as ChromeService

# --- Logging Setup ---
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create handlers
c_handler = logging.StreamHandler(sys.stdout) # Console handler
f_handler = logging.FileHandler('monitor.log') # File handler
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)

# Add handlers to the logger
if not logger.handlers:
    logger.addHandler(c_handler)
    logger.addHandler(f_handler)


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
        logger.info(f"Sent notification: {message}")
    except Exception as e:
        logger.error(f"Error sending ntfy notification: {e}")

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
            logger.error(f"Error parsing date string '{date_str}': {e}")
            return None

def check_for_appointments(rmv_url, ntfy_url, locations_to_monitor, state):
    """The core logic for checking appointments and sending notifications."""
    logger.info(f"--- Running RMV Appointment Check ---")
    
    live_data = get_rmv_data(rmv_url, locations_to_monitor)
    if not live_data:
        logger.warning("Could not fetch live appointment data.")
        return state

    for location_data in live_data:
        location_id = str(location_data['id'])
        location_name = location_data['service_center']
        new_date_str = location_data['earliest_date']
        new_date = parse_date(new_date_str)

        if not new_date:
            logger.info(f"No appointments found for {location_name}.")
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
            logger.info(f"No change for {location_name}. Earliest is still {last_known_date_str}")
    
    save_json(state, STATE_FILE)
    logger.info("--- Check complete ---")
    return state

def run_monitor():
    """Main monitoring loop."""
    load_dotenv()

    # --- Configuration Healing ---
    rmv_url = os.getenv("RMV_URL")
    if not rmv_url:
        logger.warning("RMV_URL not found in .env file.")
        rmv_url = prompt_for_rmv_url()

    ntfy_url = os.getenv("NTFY_URL")
    if not ntfy_url:
        logger.warning("NTFY_URL not found in .env file.")
        ntfy_url = prompt_for_ntfy_url()

    locations_to_monitor_ids_str = os.getenv("LOCATIONS_TO_MONITOR")
    if not locations_to_monitor_ids_str:
        logger.warning("LOCATIONS_TO_MONITOR not found in .env file.")
        locations_to_monitor_ids_str = prompt_for_locations(rmv_url)

    frequency_minutes_str = os.getenv("CHECK_FREQUENCY_MINUTES")
    if not frequency_minutes_str:
        logger.warning("CHECK_FREQUENCY_MINUTES not found in .env file.")
        frequency_minutes_str = str(prompt_for_frequency())
    
    locations_to_monitor_ids = locations_to_monitor_ids_str.split(',')
    frequency_minutes = int(frequency_minutes_str)

    # --- Fetch Location Names ---
    logger.info("Fetching all location data for friendly names...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = None
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        all_locations_data = get_all_locations(driver, rmv_url)
    finally:
        if driver:
            driver.quit()
    
    if not all_locations_data:
        logger.error("Could not fetch location data. Exiting.")
        sys.exit(1)

    location_id_to_name_map = {loc['id']: loc['service_center'] for loc in all_locations_data}
    locations_to_monitor = [
        {'id': loc_id, 'service_center': location_id_to_name_map.get(loc_id, f"ID-{loc_id}")} 
        for loc_id in locations_to_monitor_ids
    ]

    # --- State Reset ---
    if os.path.exists(STATE_FILE):
        reset_state_choice = input("Do you want to delete the existing state.json file? [y/N]: ").lower()
        if reset_state_choice == 'y':
            os.remove(STATE_FILE)
            logger.info("Deleted state.json")
    
    state = load_json(STATE_FILE)

    logger.info(f"Starting monitor. Will check every {frequency_minutes} minutes.")

    while True:
        try:
            state = check_for_appointments(rmv_url, ntfy_url, locations_to_monitor, state)
        except Exception as e:
            logger.error("An unexpected error occurred during the check:", exc_info=True)
            logger.warning("The monitor will continue running.")
        
        logger.info(f"Sleeping for {frequency_minutes} minutes...")
        time.sleep(frequency_minutes * 60)

if __name__ == "__main__":
    run_monitor()
