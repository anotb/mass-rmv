import argparse
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def get_locations(driver, wait):
    """Gets all location elements from the page."""
    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "QflowObjectItem")))
        return driver.find_elements(By.CLASS_NAME, "QflowObjectItem")
    except TimeoutException:
        print("Error: Could not find location elements on the page.", file=sys.stderr)
        return []

def get_earliest_date(driver, wait):
    """Extracts the earliest available date and time from the page."""
    try:
        day_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "DateTimeGrouping-Day")))
        day_text = ' '.join([p.text for p in day_element.find_elements(By.TAG_NAME, "p")])
        time_element = driver.find_element(By.CLASS_NAME, "ServiceAppointmentDateTime")
        time_text = time_element.text
        return f"{day_text}, {time_text}"
    except TimeoutException:
        try:
            no_appt_msg = driver.find_element(By.XPATH, "//*[contains(text(), 'no available appointments')]")
            if no_appt_msg:
                return "No Appointments Available"
        except NoSuchElementException:
            return "No Date Found"
    except Exception as e:
        return f"Error finding date: {e}"

def setup_env_file(url=None):
    """Runs an interactive setup to create the .env file."""
    print("--- RMV Appointment Checker Setup ---")
    
    if not url:
        url = input("Enter your custom RMV URL: ").strip()

    ntfy_url = input("Enter your ntfy URL (e.g., https://ntfy.sh/your-topic): ").strip()

    print("Fetching available RMV locations...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)
    driver.get(url)
    
    all_location_elements = get_locations(driver, wait)
    all_locations = []
    for i, el in enumerate(all_location_elements):
        all_locations.append({
            "number": i + 1,
            "id": el.get_attribute('data-id'),
            "service_center": el.text.split('\n')[0].strip(),
        })
    driver.quit()

    print("Available Locations:")
    for loc in all_locations:
        print(f"  {loc['number']}: {loc['service_center']}")

    selected_numbers_str = input("Enter the numbers of the locations you want to monitor (comma-separated): ")
    selected_numbers = [int(n.strip()) for n in selected_numbers_str.split(',')]
    
    locations_to_monitor = [loc for loc in all_locations if loc['number'] in selected_numbers]
    location_ids_to_monitor = [loc['id'] for loc in locations_to_monitor]

    with open('.env', 'w') as f:
        f.write(f"RMV_URL={url}\n")
        f.write(f"NTFY_URL={ntfy_url}\n")
        f.write(f"LOCATIONS_TO_MONITOR={','.join(location_ids_to_monitor)}\n")
    
    print(f"\nConfiguration saved to .env file.")
    return True


def get_rmv_data(url, locations_to_check_by_id=None):
    """
    Initializes a headless Chrome browser and scrapes appointment data for the specified locations.
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/555.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/555.36")

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)
    results = []

    try:
        num_to_check = len(locations_to_check_by_id)
        for i, location in enumerate(locations_to_check_by_id):
            driver.get(url)
            
            element_to_click = wait.until(EC.presence_of_element_located((By.XPATH, f"//button[@data-id='{location['id']}']")))
            
            location_name = location['service_center']
            print(f"Checking {i+1}/{num_to_check}: {location_name}...")
            driver.execute_script("arguments[0].click();", element_to_click)

            earliest_date = get_earliest_date(driver, wait)
            
            results.append({
                "id": location['id'],
                "service_center": location_name,
                "earliest_date": earliest_date
            })

    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
    finally:
        driver.quit()
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the interactive setup for the RMV appointment checker.")
    parser.add_argument("--url", help="The custom URL from the RMV email (optional).")
    args = parser.parse_args()
    setup_env_file(args.url)

