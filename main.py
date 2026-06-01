import requests
import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
from PIL import Image, ImageTk  # To add the logo
import pytz  # For timezone conversions
import urllib.request
import json

# OpenWeatherMap API key and base URL
owm_api_key = "8d4e8f807af8f877a9b46931b17a21cc"
owm_base_url = "http://api.openweathermap.org/data/2.5/weather?"

# VisualCrossing API for hourly weather
vc_api_key = "ZNYH45SCWGSZHQLV29WLD4ZCM"
vc_base_url = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/"

# Function to get the weather data using city name
def get_weather(city_name):
    global temp_label, condition_label, wind_label, sunrise_label, sunset_label, current_time_label

    # OpenWeatherMap API for current weather
    complete_url = f"{owm_base_url}q={city_name}&appid={owm_api_key}&units=metric"
    response = requests.get(complete_url)
    data = response.json()

    if data["cod"] != "404":
        city_info = data
        # Get current time from system
        timezone_offset = data["timezone"]  # in seconds
        local_time = datetime.utcnow() + timedelta(seconds=timezone_offset)

        # Display current local time and date
        current_time_label.config(text=f"Current Time: {local_time.strftime('%Y-%m-%d %I:%M %p')}")

        # Display city details
        city_label.config(text=f"{city_info['name']}, {city_info['sys']['country']}")
        temp_label.config(text=f"Temperature: {city_info['main']['temp']}°C")
        condition_label.config(text=f"Weather: {city_info['weather'][0]['description'].capitalize()}")
        wind_label.config(text=f"Wind Speed: {city_info['wind']['speed']} m/s")

        # Convert sunrise and sunset times to local time
        sunrise_time_utc = datetime.utcfromtimestamp(city_info['sys']['sunrise'])
        sunset_time_utc = datetime.utcfromtimestamp(city_info['sys']['sunset'])
        sunrise_time_local = sunrise_time_utc + timedelta(seconds=timezone_offset)
        sunset_time_local = sunset_time_utc + timedelta(seconds=timezone_offset)

        sunrise_label.config(text=f"Sunrise: {sunrise_time_local.strftime('%I:%M %p')}")
        sunset_label.config(text=f"Sunset: {sunset_time_local.strftime('%I:%M %p')}")

        # Get hourly forecast from VisualCrossing API
        get_hourly_forecast(city_name, local_time)

    else:
        messagebox.showerror("Error", "City Not Found. Please enter a valid city name.")


# Function to get hourly forecast for the next 24 hours using VisualCrossing API
def get_hourly_forecast(city_name, current_time):
    try:
        complete_url = f"{vc_base_url}{city_name}?unitGroup=metric&include=hours%2Cdays&key={vc_api_key}&contentType=json"
        ResultBytes = urllib.request.urlopen(complete_url)
        jsonData = json.load(ResultBytes)

        # Clear previous forecast
        for widget in forecast_frame.winfo_children():
            widget.destroy()

        # Display hourly forecast in a grid for the next 24 hours
        hours = jsonData['days'][0]['hours']

        for i, hour_data in enumerate(hours[:24]):
            time = (current_time + timedelta(hours=i)).strftime('%I:%M %p')
            temp = f"{hour_data['temp']}°C"
            condition = hour_data['conditions'].capitalize()

            # Create a frame for each hourly forecast
            hour_frame = tk.Frame(forecast_frame, bg="lightblue", padx=5, pady=5)
            hour_frame.grid(row=i // 6, column=i % 6, padx=10, pady=10)

            # Time label
            time_label = tk.Label(hour_frame, text=time, font=("Arial", 10, "bold"), bg="lightblue")
            time_label.pack()

            # Weather icon (placeholder here, you can replace with actual icons)
            icon_label = tk.Label(hour_frame, text="☀️", font=("Arial", 20), bg="lightblue")
            icon_label.pack()

            # Temperature label
            temp_label = tk.Label(hour_frame, text=temp, font=("Arial", 10), bg="lightblue")
            temp_label.pack()

            # Condition label
            condition_label = tk.Label(hour_frame, text=condition, font=("Arial", 10), bg="lightblue")
            condition_label.pack()

    except urllib.error.HTTPError as e:
        ErrorInfo = e.read().decode()
        print('Error code: ', e.code, ErrorInfo)
        sys.exit()
    except urllib.error.URLError as e:
        ErrorInfo = e.read().decode()
        print('Error code: ', e.code, ErrorInfo)
        sys.exit()


# Function to handle the button click and fetch weather
def get_forecast():
    city_name = city_entry.get()
    if city_name:
        get_weather(city_name)
    else:
        messagebox.showwarning("Input Error", "Please enter a city name.")


# Set up the main window
root = tk.Tk()
root.title("Creative Weather App")
root.geometry("900x800")
root.configure(bg="#e0f7fa")
root.resizable(True, True)

# Add a logo image at the top (you need a logo file in your directory)
try:
    logo = Image.open("logo.png")  # Replace "logo.png" with the path to your logo
    logo = logo.resize((100, 100), Image.ANTIALIAS)
    logo_image = ImageTk.PhotoImage(logo)
    logo_label = tk.Label(root, image=logo_image, bg="#e0f7fa")
    logo_label.pack(pady=10)
except FileNotFoundError:
    logo_label = tk.Label(root, text="Weather App", font=("Arial", 20, "bold"), fg="white", bg="#0288d1")
    logo_label.pack(pady=10)

# Header Frame
header_frame = tk.Frame(root, bg="#0288d1", padx=10, pady=10)
header_frame.pack(fill="x")

# Header Label
header_label = tk.Label(header_frame, text="Weather Forecast", font=("Arial", 24, "bold"), fg="white", bg="#0288d1")
header_label.pack()

# Input Frame
input_frame = tk.Frame(root, bg="#e0f7fa", padx=10, pady=10)
input_frame.pack()

# City Entry and Button
city_entry = tk.Entry(input_frame, width=30, font=("Arial", 14))
city_entry.grid(row=0, column=0, padx=10)

forecast_button = tk.Button(input_frame, text="Get Weather", font=("Arial", 14), command=get_forecast, bg="#0288d1", fg="white")
forecast_button.grid(row=0, column=1)

# City Info Frame
info_frame = tk.Frame(root, bg="#e0f7fa", padx=10, pady=10)
info_frame.pack()

# City and Weather Info
city_label = tk.Label(info_frame, text="", font=("Arial", 16, "bold"), bg="#e0f7fa")
city_label.grid(row=0, column=0, sticky="w")

temp_label = tk.Label(info_frame, text="", font=("Arial", 14), bg="#e0f7fa")
temp_label.grid(row=1, column=0, sticky="w")

condition_label = tk.Label(info_frame, text="", font=("Arial", 14), bg="#e0f7fa")
condition_label.grid(row=2, column=0, sticky="w")

wind_label = tk.Label(info_frame, text="", font=("Arial", 14), bg="#e0f7fa")
wind_label.grid(row=3, column=0, sticky="w")

sunrise_label = tk.Label(info_frame, text="", font=("Arial", 14), bg="#e0f7fa")
sunrise_label.grid(row=4, column=0, sticky="w")

sunset_label = tk.Label(info_frame, text="", font=("Arial", 14), bg="#e0f7fa")
sunset_label.grid(row=5, column=0, sticky="w")

# Current Time Label
current_time_label = tk.Label(info_frame, text="", font=("Arial", 14), bg="#e0f7fa")
current_time_label.grid(row=6, column=0, sticky="w")

# Forecast Frame
forecast_frame = tk.Frame(root, bg="lightblue", padx=10, pady=10)
forecast_frame.pack(fill="both", expand=True)

# Run the Tkinter event loop
root.mainloop()
