# RMV Appointment Checker & Notifier

A simple tool to monitor the Massachusetts RMV website for earlier appointment times and send notifications via ntfy.

## Features

*   Continuously monitors selected RMV locations for new appointment slots.
*   Sends instant notifications to your devices using a self-hosted or public [ntfy](https://ntfy.sh) server.
*   Securely manages configuration using a `.env` file, keeping your sensitive URLs out of version control.
*   Interactive command-line setup to create your `.env` file.
*   Remembers the last seen appointment time to avoid duplicate notifications.

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

3.  **Run the monitor:**
    The first time you run the script, it will automatically guide you through a one-time interactive setup.
    ```bash
    python3 monitor.py
    ```

## Usage

### Running the Monitor

Simply run the monitor script. 

```bash
python3 monitor.py
```

If it's your first time running it, or if any configuration is missing, it will automatically guide you through a one-time setup to get the information it needs.

On subsequent runs, it will use your saved settings to start checking immediately. You will only be asked if you want to reset your notification history.

### Running in the Background

To keep the monitor running after you close your terminal, use `nohup`:

```bash
nohup python3 monitor.py &
```

All detailed, timestamped output will be saved to a `monitor.log` file. To stop the monitor, find its Process ID (PID) and use the `kill` command:

```bash
# Find the process ID
ps aux | grep monitor.py

# Stop the process
kill <PID>
```

