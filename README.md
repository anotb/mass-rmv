# RMV Appointment Checker & Notifier

This tool helps you find earlier appointment times at the Massachusetts RMV. It monitors your selected RMV locations and sends a notification to your phone or other devices via a [ntfy](https://ntfy.sh) server.

## How It Works

The tool uses a web scraper to check the official RMV appointment scheduling site. It consists of two main parts:

1.  `rmv_checker.py`: The core script that can be run with flags for one-off checks or to initiate the interactive setup.
2.  `monitor.py`: The main script you will run to set up your configuration and start the continuous monitoring process.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Install Python dependencies:**
    It's recommended to use a virtual environment.
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

## Setup & Usage

The primary way to use this tool is to run the `monitor.py` script.

```bash
python3 monitor.py
```

### First-Time Setup & Resetting
If you are running the monitor for the first time, or if you want to reset your configuration, the script will prompt you. Answering 'y' will delete your existing `config.json` and `state.json` files and guide you through the interactive setup process. You will be prompted to enter:
*   **Your custom RMV URL:** The unique URL you received in your email from the RMV.
*   **Your ntfy URL:** The full URL for your ntfy topic (e.g., `https://ntfy.sh/your-topic` or a self-hosted URL).
*   **Locations to monitor:** You will be shown a list of all available RMV locations. Enter the numbers of the locations you wish to track, separated by commas.

This will create a `config.json` file with your settings. To re-run this setup, you can either delete `config.json` manually or run `python3 rmv_checker.py`.

### Starting the Monitor
After the setup, the script will ask you how often you want to check for new appointments.

```
How often to check for appointments (in minutes)? [default: 5]: 
```

Enter your desired frequency (in minutes) and press Enter. The monitor will then start running and will check for appointments at the interval you specified.

### Running in the Background

To keep the monitor running after you close your terminal, you should run it in the background. The recommended way to do this is with `nohup` (no hang up), which also logs the output to a file.

```bash
nohup python3 monitor.py &
```

This command will:
*   Start `monitor.py` in the background (`&`).
*   Prevent it from being stopped when you close the terminal (`nohup`).
*   Create a file named `nohup.out` in the same directory, which will contain all the printed output from the script.

To stop the monitor, you will need to find its Process ID (PID) and kill it:
```bash
# Find the process
ps aux | grep monitor.py

# Kill the process (replace <PID> with the number from the previous command)
kill <PID>
```

### Manual Checking

You can perform a one-off check by running the `rmv_checker.py` script. This is useful for testing or quick checks without using the monitoring functionality. This will run the interactive setup if no `config.json` exists.

```bash
python3 rmv_checker.py
```

### Resetting Notifications

The monitor will only notify you once for each new earliest appointment time it finds. If you miss booking an appointment and want to be notified about it again, you can reset the tool's memory by deleting the `state.json` file. You will be prompted to do this automatically when you start `monitor.py`.
