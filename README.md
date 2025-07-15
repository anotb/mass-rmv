# RMV Appointment Checker & Notifier

A simple tool to monitor the Massachusetts RMV website for earlier appointment times and send notifications via ntfy.

## Features

*   Continuously monitors selected RMV locations for new appointment slots.
*   Sends instant notifications to your devices using a self-hosted or public [ntfy](https://ntfy.sh) server.
*   Interactive command-line setup to configure your custom RMV URL, ntfy topic, and locations.
*   Remembers the last seen appointment time to avoid duplicate notifications.
*   Option to easily reset the configuration and start fresh.

## Getting Started

### Prerequisites

*   Python 3
*   Git

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/anotb/mass-rmv.git
    cd mass-rmv
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Run the interactive setup:**
    The first time you run the monitor, it will guide you through a setup process.
    ```bash
    python3 monitor.py
    ```
    You will be asked for:
    *   Your unique RMV URL (from the email).
    *   Your ntfy topic URL.
    *   The specific RMV locations you want to monitor.

## Usage

### Running the Monitor

After the initial setup, run the monitor script to start checking for appointments. You'll be asked how frequently (in minutes) you want to check.

```bash
python3 monitor.py
```

### Running in the Background

To keep the monitor running after you close your terminal, use `nohup`:

```bash
nohup python3 monitor.py &
```

All output will be saved to a `nohup.out` file in the same directory. To stop the monitor, find its Process ID (PID) and use the `kill` command:

```bash
# Find the process ID
ps aux | grep monitor.py

# Stop the process
kill <PID>
```

### Resetting Configuration

If you need to change your settings (like the RMV URL or locations), you can trigger the interactive setup again. When you start the monitor, it will ask if you want to delete the existing configuration. Simply answer `y`.

```bash
python3 monitor.py
> Do you want to delete the existing config and state files? [y/N]: y
```