import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timezone, timedelta

# Load the API key from .env so we don't hardcode sensitive info
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"


# I created a reusable helper function to fetch forecast data for any zip code.
# This way I don't repeat the same API call logic in every question.
def get_forecast(zip_code, units="imperial"):
    params = {
        "zip": f"{zip_code},us",
        "appid": API_KEY,
        "units": units  # imperial=Fahrenheit, metric=Celsius, standard=Kelvin
    }
    response = requests.get(BASE_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data for {zip_code}: {response.json()['message']}")
        return None


# ─────────────────────────────────────────────
# Q1: Daily average temperature difference in Fahrenheit
# ─────────────────────────────────────────────

# The forecast API returns data in 3-hour intervals, so to get a daily average
# I grouped all the temperature readings by date and averaged them out.
def q1_daily_avg_temp_difference():
    data1 = get_forecast("94203", units="imperial")
    data2 = get_forecast("94102", units="imperial")

    if not data1 or not data2:
        return

    city1 = data1["city"]["name"]
    city2 = data2["city"]["name"]

    def daily_avg(data):
        temps_by_day = {}
        for entry in data["list"]:
            date = entry["dt_txt"].split(" ")[0]
            temps_by_day.setdefault(date, []).append(entry["main"]["temp"])
        return {date: sum(temps)/len(temps) for date, temps in temps_by_day.items()}

    avg1 = daily_avg(data1)
    avg2 = daily_avg(data2)

    print("\n── Q1: Daily Average Temperature Difference (°F) ──")
    for date in avg1:
        if date in avg2:
            diff = avg1[date] - avg2[date]
            if diff < 0:
                print(f"It is {abs(diff):.1f}°F colder in {city1} than in {city2} on {date}")
            else:
                print(f"It is {diff:.1f}°F warmer in {city1} than in {city2} on {date}")


# ─────────────────────────────────────────────
# Q2: Next hour temperature difference in Celsius
# ─────────────────────────────────────────────

# The API gives forecast data in 3-hour blocks, so I find the first entry
# that is at or after the next full hour from when this function is called.
def q2_next_hour_temp_difference():
    data1 = get_forecast("94203", units="metric")
    data2 = get_forecast("94102", units="metric")

    if not data1 or not data2:
        return

    city1 = data1["city"]["name"]
    city2 = data2["city"]["name"]

    # Figure out what the next full hour is in UTC
    now = datetime.now(timezone.utc)
    next_hour = now.replace(minute=0, second=0, microsecond=0)
    if now.minute > 0:
        next_hour += timedelta(hours=1)

    # Find the first forecast entry that falls on or after the next hour
    def get_temp_for_next_hour(data):
        for entry in data["list"]:
            entry_time = datetime.strptime(
                entry["dt_txt"], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=timezone.utc)
            if entry_time >= next_hour:
                return entry["main"]["temp"], entry["dt_txt"]
        return None, None

    temp1, time1 = get_temp_for_next_hour(data1)
    temp2, time2 = get_temp_for_next_hour(data2)

    print("\n── Q2: Next Hour Temperature Difference (°C) ──")
    if temp1 is not None and temp2 is not None:
        diff = temp1 - temp2
        if diff < 0:
            print(f"At {time1} UTC, it is {abs(diff):.1f}°C colder in {city1} than in {city2}")
        else:
            print(f"At {time1} UTC, it is {diff:.1f}°C warmer in {city1} than in {city2}")


# ─────────────────────────────────────────────
# Q3: 5-day combined forecast averages in Kelvin
# ─────────────────────────────────────────────

# For each day I separated day and night readings using the "pod" field
# (pod = "d" for day, "n" for night) and averaged both cities together.
def q3_five_day_combined_forecast():
    data1 = get_forecast("94203", units="standard")  # standard unit = Kelvin
    data2 = get_forecast("94102", units="standard")

    if not data1 or not data2:
        return

    # Group forecast entries by date
    def group_by_day(data):
        days = {}
        for entry in data["list"]:
            date = entry["dt_txt"].split(" ")[0]
            days.setdefault(date, []).append(entry)
        return days

    days1 = group_by_day(data1)
    days2 = group_by_day(data2)

    print("\n── Q3: 5-Day Combined Forecast (Kelvin) ──")

    for date in list(days1.keys())[:5]:
        if date not in days2:
            continue

        entries1 = days1[date]
        entries2 = days2[date]

        # Separate day and night temps using the pod field
        def avg_temp_by_pod(entries, pod):
            temps = [
                e["main"]["temp"]
                for e in entries
                if e.get("sys", {}).get("pod") == pod
            ]
            return sum(temps) / len(temps) if temps else None

        day_temp1 = avg_temp_by_pod(entries1, "d")
        day_temp2 = avg_temp_by_pod(entries2, "d")
        night_temp1 = avg_temp_by_pod(entries1, "n")
        night_temp2 = avg_temp_by_pod(entries2, "n")

        # Combine both cities into one average
        def combined(a, b):
            if a is not None and b is not None:
                return (a + b) / 2
            return a or b

        combined_day = combined(day_temp1, day_temp2)
        combined_night = combined(night_temp1, night_temp2)

        # Humidity and cloudiness averaged across both cities
        all_entries = entries1 + entries2
        avg_humidity = sum(e["main"]["humidity"] for e in all_entries) / len(all_entries)
        avg_clouds = sum(e["clouds"]["all"] for e in all_entries) / len(all_entries)

        print(f"\n📅 {date}")
        if combined_day:
            print(f"  🌤  Combined Avg Day Temp   : {combined_day:.2f}K")
        else:
            print(f"  🌤  Combined Avg Day Temp   : N/A")
        if combined_night:
            print(f"  🌙  Combined Avg Night Temp : {combined_night:.2f}K")
        else:
            print(f"  🌙  Combined Avg Night Temp : N/A")
        print(f"  💧  Combined Avg Humidity   : {avg_humidity:.1f}%")
        print(f"  ☁️   Combined Avg Cloudiness : {avg_clouds:.1f}%")


# Run all three questions
q1_daily_avg_temp_difference()
q2_next_hour_temp_difference()
q3_five_day_combined_forecast()