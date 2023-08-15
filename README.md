# Massachusetts RMV Appointment Checker

This tool helps you automatically check for the earliest available dates at your chosen Massachusetts RMV service centers. It will notify you if a new earliest date becomes available.

## Open and Run in Google Colab

To run the notebook in Google Colab, simply click on the badge below:

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/anotb/mass-rmv/blob/main/rmv_checker.ipynb)

After opening the notebook in Colab, you can execute the cells to run the code. Make sure to follow the instructions provided in the notebook.

## Instructions

1. **Setup and Dependencies**:
   - If you're using this on Google Colab, the first few cells will help you set up the necessary dependencies.
   - If running locally, ensure you have the required packages installed (mainly Selenium).

2. **Obtaining a Custom URL**:
   - Navigate to [Massachusetts RMV](https://atlas-myrmv.massdot.state.ma.us/myrmv/_/) and proceed with booking an appointment for scheduling a service center visit. Complete the form, and upon confirmation, you will receive an email containing the custom URL. 
   - Replace the placeholder URL in the specified cell with the URL from your email.

3. **Selecting Service Centers**:
   - Once the URL is loaded in the tool, it will display a list of available service centers from the Massachusetts RMV.
   - You can open the custom URL in a browser to view a map, which might give you a better sense of which service centers you'd like to choose.
   - After getting an idea, return to this tool and select the centers you want to track by entering their corresponding numbers, separated by commas (e.g., `1,4,7`).

4. **Monitoring**:
   - After selecting the centers, the tool will begin monitoring the specified service centers for appointment availability.
   - It will notify you if a new earliest date becomes available.

5. **Alerts**:
   - When running on Google Colab, you'll receive a browser alert if an earlier appointment date is found.

6. **Continuous Monitoring**:
   - The tool will pause for 30 seconds between checks to avoid overwhelming the server. You can adjust this time if necessary.

7. **Copying to Your Colab Workspace**:
   - If you're viewing a shared version of this notebook, it is in a read-only mode. To run or modify it, you'll need to save a copy to your own Google Drive. This ensures your session remains private.

## Usage

Simply follow the instructions in each cell of the notebook. Make sure to replace the placeholder URL with your custom URL from the Massachusetts RMV email and select the service centers you wish to monitor.
