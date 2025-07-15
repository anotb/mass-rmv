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

3.  **Run the interactive setup:**
    This will create a `.env` file in the project directory to store your configuration.
    ```bash
    python3 rmv_checker.py
    ```
    You will be asked for:
    *   Your unique RMV URL (from the email).
    *   Your ntfy topic URL.
    *   The specific RMV locations you want to monitor.

## Usage

### Running the Monitor

Once your `.env` file is created, you can start the monitor. You'll be asked how frequently (in minutes) you want to check.

```bash
python3 monitor.py
```

### Running in the Background

To keep the monitor running after you close your terminal, use `nohup`:

```bash
nohup python3 monitor.py &
```

All output will be saved to a `nohup.out` file. To stop the monitor, find its Process ID (PID) and use the `kill` command:

```bash
# Find the process ID
ps aux | grep monitor.py

# Stop the process
kill <PID>
```

### Resetting Configuration

To change your settings (like the RMV URL or locations), simply run the interactive setup again. This will overwrite the existing `.env` file.

```bash
python3 rmv_checker.py
```

You can also reset the notification history by deleting the `state.json` file. The monitor will prompt you to do this automatically on startup if the file exists.
