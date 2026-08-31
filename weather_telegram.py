# weather_telegram.py — Prague weather, written by AI, sent to Telegram.
# Flow: get today's forecast (7:30 AM + 4:30 PM) -> ask Gemini to write a
# friendly message (jacket tip if morning is below 17 C) -> send to Telegram.

import os
from datetime import date

import requests
from google import genai

# --- Secrets (provided by GitHub Actions; never written in the code) ---
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]      # from @BotFather
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]  # from @userinfobot
GEMINI_API_KEY = os.environ["GEMINI_API_KEY"]      # from Google AI Studio (free)

# --- Location: Prague ---
LATITUDE = 50.08
LONGITUDE = 14.44
CITY_NAME = "Prague"


def get_forecast():
    """Fetch today's hourly forecast and pull out the 7:30 AM and 4:30 PM slots."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LATITUDE,
        "longitude": LONGITUDE,
        "hourly": "temperature_2m,cloud_cover,wind_speed_10m",
        "timezone": "Europe/Prague",
        "forecast_days": 1,
    }
    hourly = requests.get(url, params=params).json()["hourly"]

    today = date.today().isoformat()  # e.g. "2026-08-31"

    def slot(hour):
        """Return (temp, cloud%, wind) for a given hour today, e.g. hour=7."""
        target = f"{today}T{hour:02d}:00"
        i = hourly["time"].index(target)
        return {
            "temp": hourly["temperature_2m"][i],
            "cloud": hourly["cloud_cover"][i],
            "wind": hourly["wind_speed_10m"][i],
        }

    return slot(7), slot(16)  # ~7:30 AM (07:00 slot), ~4:30 PM (16:00 slot)


def write_message(morning, afternoon):
    """Ask Gemini (Google's free AI) to turn the numbers into a friendly message."""
    client = genai.Client(api_key=GEMINI_API_KEY)

    facts = (
        f"City: {CITY_NAME}\n"
        f"Around 7:30 AM  -> temperature {morning['temp']} C, "
        f"cloud cover {morning['cloud']}%, wind {morning['wind']} km/h\n"
        f"Around 4:30 PM  -> temperature {afternoon['temp']} C, "
        f"cloud cover {afternoon['cloud']}%, wind {afternoon['wind']} km/h"
    )

    prompt = (
        "You write a short, warm daily weather message for me. Use these facts:\n\n"
        f"{facts}\n\n"
        "Rules:\n"
        "- Mention the 7:30 AM temperature and the 4:30 PM temperature.\n"
        "- For 4:30 PM, describe conditions in plain words: say 'cloudy' if cloud "
        "cover is above 60%, and 'windy' if wind is above 20 km/h.\n"
        "- If the 7:30 AM temperature is below 17 C, tell me to wear a jacket.\n"
        "- Keep it under 4 short lines. A couple of weather emojis are welcome. "
        "Reply with ONLY the message."
    )

    response = client.models.generate_content(
        model="gemini-2.5-flash",  # free tier, fast
        contents=prompt,
    )
    return response.text.strip()


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
morning, afternoon = get_forecast()
message = write_message(morning, afternoon)
print(message)                 # also print so we can see it in the Actions log
send_to_telegram(message)
