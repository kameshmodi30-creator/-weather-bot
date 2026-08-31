# weather_telegram.py — Stage 3: fetch Prague weather and send it to Telegram
# Uses Open-Meteo (free) + your own Telegram bot.

import os
import requests

# =========================================================
# The token & chat id are read from "environment variables" (secrets),
# NOT written in the code — so this file is safe to put on public GitHub.
# GitHub Actions provides them from the repo's Secrets. For a local test,
# set them in your terminal first (see note at bottom of file).
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]      # from @BotFather
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]  # from @userinfobot
# =========================================================

# --- Location: Prague ---
LATITUDE = 50.08
LONGITUDE = 14.44
CITY_NAME = "Prague"


def get_weather():
    """Ask Open-Meteo for the current weather and return a text message."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m",
    }
    data = requests.get(url, params=params).json()
    c = data["current"]

    message = (
        f"Good morning! Weather in {CITY_NAME}:\n"
        f"Temperature: {c['temperature_2m']} C\n"
        f"Humidity: {c['relative_humidity_2m']}%\n"
        f"Wind: {c['wind_speed_10m']} km/h"
    )
    return message


def send_to_telegram(message):
    """Send a text message to your Telegram chat via your bot."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    params = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    response = requests.get(url, params=params)
    if response.ok:
        print("Message sent to Telegram!")
    else:
        print("Failed to send. Telegram said:", response.text)


# --- Run it ---
weather_message = get_weather()
print(weather_message)          # also print to screen so you can see it
send_to_telegram(weather_message)
