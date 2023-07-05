# Backend README
This project provides a dashboard that displays various measurements collected by a climate sensor robot, including CO2, temperature, humidity, particulate matter and air pressure. Additionally, the dashboard shows the location of the sensor robot.

The data displayed on the dashboard is collected from TheThingsNetwork, where the climate sensor robot sends its data and location. The data is then stored in a PostgreSQL data server for easy access and analysis.

## Installation process (Windows, local)

1. Download Python 3.9: https://www.python.org/downloads/release/python-3917/
2. Download the latest release of dashboard.
3. Open Powershell and navigate to folder of the dashboard.
4. Create a virtual environment with: ```python -m venv .venv```
5. Enter the virtual environment with: ```.\.venv\Scripts\Activate.ps1```
6. Install required modules with: ```pip install -r requirements.txt```
7. Setup the database connection with: ```flask db migrate```


## Usage
To launch and access the website:
1. Launch the server with: ```flask run```
2. Go to ```localhost:5000``` in your browser.
3. Login with your account.

Once you have logged in and accessed the Home page you can use the links in the header to access different pages.

### Home
Here you can see the most recent recorded data from the sensor robot, a map that displays the current location of the robot, a heatmap displaying the temperature in different areas of the map, and a list of status notifications on the left.

### Statistieken
Here you can display sensor data for various dates and regions:
- Use the buttons on the left to quickly see the data for a pre-set range of time.
- Use the datetime input below the buttons to set a custom time range for the data.
- Use the checkboxes on the map to enable or disable the display of data for certain regions.

### Abonneren
Here you can subscribe or unsubscribe to receive the status notifications through email by entering your email address and pressing the corresponding button.

### Log uit
This link will log you out of your account and take you back to the login page.



## **Technologies and Dependencies**

This system is built using the following technologies:

- Flask 2.2.x
- Python 3.9
