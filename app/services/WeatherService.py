import requests
from flask import current_app

class WeatherService:
    @staticmethod
    def getCurrentWeatherInfo(latitude: float, longitude: float):
        url = "https://api.openweathermap.org/data/2.5/weather"
        key = current_app.config.get("WEATHER_API_KEY") 
        params = {
            "lat": latitude,
            "lon": longitude,
            "appid": key,
            "units": "metric"
        }

        response = requests.get(url, params=params)
        data = response.json()

        if response.status_code != 200 or "main" not in data:
            return {"error": data.get("message", "Failed to fetch weather data.")}

        weather = data.get("weather", [{}])[0]
        rain = data.get("rain", {})
        snow = data.get("snow", {})

        return {
            "temperature_c": data["main"].get("temp"),
            "humidity": data["main"].get("humidity"),
            "wind_ms": round(data["wind"].get("speed", 0), 2),
            "precip_mm": rain.get("1h", 0.0) + snow.get("1h", 0.0),
            "condition": weather.get("description"),
            "condition_icon": f"http://openweathermap.org/img/wn/{weather.get('icon')}@2x.png" if weather.get("icon") else None,
        }
     
    
    @staticmethod
    def mapWeatherCondition(description: str, wind_speed: float) -> str:
        """Used for weather_condition_today"""
        description = description.lower()
        if wind_speed > 7.0:
            return "WINDY"
        if any(word in description for word in ["rain", "thunderstorm", "shower", "snow", "mist", "drizzle"]):
            return "RAINY"
        elif "clear" in description:
            return "SUNNY"
        elif any(word in description for word in ["cloud", "overcast", "haze"]):
            return "NORMAL"
        else:
            return "NORMAL"

    @staticmethod
    def mapYieldWeatherCondition(description: str, wind_speed: float) -> str:
        """
        Maps to one of: ['Sunny', 'Rainy', 'Cloudy']
        Used for appending to weather_history
        """
        description = description.lower()
        if wind_speed > 7.0:
            return "Cloudy" 

        if any(word in description for word in ["rain", "thunderstorm", "shower", "snow", "mist", "drizzle"]):
            return "Rainy"
        elif "clear" in description:
            return "Sunny"
        else:
            return "Cloudy"