import argparse
import sys
import logging
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

# Use the same logger as the main monitor
logger = logging.getLogger(__name__)

def update_env_file(key, value):
    """
    Adds or updates a key-value pair in the .env file, preserving other values.
    """
    env_file = '.env'
    lines = []
    key_found = False
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            lines = f.readlines()

    with open(env_file, 'w') as f:
        for line in lines:
            if line.strip().startswith(key + '='):
                f.write(f"{key}={value}\n")
                key_found = True
            else:
                f.write(line)
        
        if not key_found:
            f.write(f"{key}={value}\n")

def get_all_locations(driver, url):
    """Gets all available RMV locations from the initial page."""
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "QflowObjectItem")))
        location_elements = driver.find_elements(By.CLASS_NAME, "QflowObjectItem")
        
        all_locations = []
        for i, el in enumerate(location_elements):
            all_locations.append({
                "number": i + 1,
                "id": el.get_attribute('data-id'),
                "service_center": el.text.split('\n')[0].strip(),
            })
        return all_locations
    except TimeoutException:
        logger.error("Could not find location elements on the page. The website may be down or has changed.")
        return []

def prompt_for_rmv_url():
    """Prompts user for the RMV URL and saves it."""
    url = input("Enter your custom RMV URL: ").strip()
    update_env_file("RMV_URL", url)
    return url

def prompt_for_ntfy_url():
    """Prompts user for the ntfy URL and saves it."""
    url = input("Enter your ntfy URL (e.g., https://ntfy.sh/your-topic): ").strip()
    update_env_file("NTFY_URL", url)
    return url

def prompt_for_locations(rmv_url):
    """Prompts user to select locations and saves their internal IDs."""
    print("Fetching available RMV locations...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = None
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        all_locations = get_all_locations(driver, rmv_url)
    finally:
        if driver:
            driver.quit()

    if not all_locations:
        logger.error("Could not fetch locations. Cannot proceed.")
        return None, None

    print("Available Locations:")
    for loc in all_locations:
        print(f"  {loc['number']}: {loc['service_center']}")

    while True:
        try:
            selected_numbers_str = input("Enter the numbers of the locations you want to monitor (comma-separated): ")
            selected_numbers = [int(n.strip()) for n in selected_numbers_str.split(',')]
            
            valid_numbers = [loc['number'] for loc in all_locations]
            if all(num in valid_numbers for num in selected_numbers):
                break
            else:
                print("Error: One or more numbers are not in the list of available locations. Please try again.", file=sys.stderr)
        except ValueError:
            print("Error: Invalid input. Please enter only numbers, separated by commas.", file=sys.stderr)
    
    locations_to_monitor = [loc for loc in all_locations if loc['number'] in selected_numbers]
    location_ids_to_monitor = [loc['id'] for loc in locations_to_monitor]
    location_ids_str = ','.join(location_ids_to_monitor)
    update_env_file("LOCATIONS_TO_MONITOR", location_ids_str)
    
    # Return both the string of IDs and the full location data used to generate it
    return location_ids_str, all_locations

def prompt_for_frequency():
    """Prompts user for the check frequency and saves it."""
    while True:
        try:
            frequency_minutes = int(input("How often to check for appointments (in minutes)? [default: 5]: ") or "5")
            break
        except ValueError:
            print("Error: Please enter a valid number.", file=sys.stderr)
    update_env_file("CHECK_FREQUENCY_MINUTES", str(frequency_minutes))
    return frequency_minutes

def setup_env_file():
    """Runs the full interactive setup to create/update the .env file."""
    print("--- Full RMV Appointment Checker Setup ---")
    rmv_url = prompt_for_rmv_url()
    prompt_for_ntfy_url()
    prompt_for_locations(rmv_url)
    prompt_for_frequency()
    print("\nConfiguration saved to .env file.")
    return True

def get_earliest_date(driver, wait):
    """
    Extracts the earliest available date and time from the page by finding the
    earliest date, clicking the corresponding 'Morning' or 'Afternoon' control,
    and then grabbing the first available time slot.
    """
    try:
        # 1. Find the container for the very first day column. This is the most reliable parent.
        first_day_column = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DateTimeGrouping-Column")))
        
        # 2. Extract the date text from within that column for the final output.
        day_text_elements = first_day_column.find_elements(By.TAG_NAME, "p")
        day_text = ' '.join([p.text for p in day_text_elements])
        day_text = day_text.strip().rstrip(',')

        # 3. Find the clickable control (Morning or Afternoon) within that same column.
        clickable_control = None
        try:
            # Prioritize 'Morning'
            clickable_control = first_day_column.find_element(By.XPATH, ".//div[contains(@class, 'Morning')]")
        except NoSuchElementException:
            try:
                # Fallback to 'Afternoon'
                clickable_control = first_day_column.find_element(By.XPATH, ".//div[contains(@class, 'Afternoon')]")
            except NoSuchElementException:
                # If no controls are found, it means no time slots are available for this day.
                return day_text

        # 4. Click the control to reveal the time slots.
        if clickable_control:
            # The 'aria-pressed' attribute tells us if the section is already open.
            if clickable_control.get_attribute('aria-pressed') == 'false':
                 driver.execute_script("arguments[0].click();", clickable_control)
            
            # 5. Wait for the associated container with time slots to be present.
            time_container_id = clickable_control.get_attribute('aria-controls')
            time_wait = WebDriverWait(driver, 5)
            
            # Wait for the first time slot div inside the correct container.
            first_time_slot = time_wait.until(EC.presence_of_element_located(
                (By.XPATH, f"//div[@id='{time_container_id}']//div[contains(@class, 'ServiceAppointmentDateTime')]")
            ))
            
            time_text = first_time_slot.text.strip()
            return f"{day_text}, {time_text}"

        return day_text

    except TimeoutException:
        # This will catch cases where no appointment columns are found at all.
        try:
            no_appt_msg = driver.find_element(By.XPATH, "//*[contains(text(), 'no available appointments')]")
            if no_appt_msg:
                return "No Appointments Available"
        except NoSuchElementException:
            return "No Date Found"
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_earliest_date", exc_info=True)
        return "Error during scraping"


def get_rmv_data(url, locations_to_check_by_id=None):
    """
    Initializes a headless Chrome browser and scrapes appointment data for the specified locations.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    
    driver = None  # Initialize driver to None
    try:
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        wait = WebDriverWait(driver, 10)
        results = []
        num_to_check = len(locations_to_check_by_id)

        for i, location in enumerate(locations_to_check_by_id):
            try:
                driver.get(url)
                
                element_to_click = wait.until(EC.presence_of_element_located((By.XPATH, f"//button[@data-id='{location['id']}']")))
                
                location_name = location['service_center']
                logger.info(f"Checking {i+1}/{num_to_check}: {location_name}...")
                driver.execute_script("arguments[0].click();", element_to_click)

                earliest_date = get_earliest_date(driver, wait)
                
                results.append({
                    "id": location['id'],
                    "service_center": location_name,
                    "earliest_date": earliest_date
                })
            except Exception as e:
                location_name = location.get('service_center', f"ID-{location['id']}")
                logger.error(f"An unexpected error occurred while checking {location_name}", exc_info=True)
                # Continue to the next location
                continue
        
        return results
    finally:
        # This will always run, ensuring the browser is closed even if errors occur.
        if driver:
            driver.quit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the interactive setup for the RMV appointment checker.")
    # This script is now primarily for a full, clean setup.
    # The monitor script handles individual missing items.
    setup_env_file()
