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

### Step 1: Initial Setup (Interactive)

You must run the monitor in your terminal one time to complete the initial setup.

```bash
python3 monitor.py
```

The script will guide you through creating a `.env` file with your configuration.

### Step 2: Running the Monitor

Once the setup is complete, you can run the monitor.

**To run in the foreground:**
```bash
python3 monitor.py
```

**To run in the background:**
```bash
nohup python3 monitor.py &
```

If you run in the background with an incomplete configuration, the script will log a fatal error to `monitor.log` and exit.

### Troubleshooting

*   **Process not staying alive?** Check the `monitor.log` file for errors. It will tell you if your setup is incomplete.
*   **Want to reset your configuration?** Simply delete the `.env` file and run the monitor interactively again.
*   **Want to reset notification history?** When you run the script interactively, it will ask if you want to delete the `state.json` file.

