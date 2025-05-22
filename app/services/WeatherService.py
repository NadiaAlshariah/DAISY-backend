import requests
import math
from flask import current_app
class WeatherService:
    #hour from 0 - 23
    @staticmethod
    def getCurrentWeatherInfo(latitude : float , longitude : float , hour : int):
        url = "http://api.weatherapi.com/v1/forecast.json"
        key = current_app.config.get("WEATHER_API_KEY")
        location = f"{latitude},{longitude}"
        params = {"q" : location,
                  "key" : key}
        response = requests.get(url, params=params)
        return WeatherService.formatResponse(response.json() , hour)

    @staticmethod
    def formatResponse(response, hour: int):
        try:
            hourly_data = response["forecast"]["forecastday"][0]["hour"][hour]
            return {
                "time": hourly_data.get("time"),
                "temperature_c": hourly_data.get("temp_c"),
                "humidity": hourly_data.get("humidity"),
                "wind_ms":  round(hourly_data.get("wind_mph", 0) * 0.44704, 2),
                "precip_mm": hourly_data.get("precip_mm"),
                "evapotranspiration" : WeatherService.getEvapotranspiration(response["forecast"]["forecastday"][0]["hour"])
            }
        except (KeyError, IndexError) as e:
            return {"error": f"Invalid response structure or hour out of range: {str(e)}"}
        

    @staticmethod
    def getEvapotranspiration(hourly_data):
        total_et = 0.0
        gamma = 0.066  # Psychrometric constant

        for hour_data in hourly_data:
            try:
                temp = hour_data.get("temp_c", 0)
                humidity = hour_data.get("humidity", 0)
                wind_mph = hour_data.get("wind_mph", 0)
                radiation = hour_data.get("short_rad", 0)
                print(radiation)
                wind_m_s = wind_mph * 0.44704  # Convert to m/s
                Rn = (radiation * 3600) / 1e6  # Convert W/m² to MJ/m²/hour
                

                # Saturation vapor pressure (es)
                es = 0.6108 * math.exp((17.27 * temp) / (temp + 237.3))
                ea = humidity * es / 100
                delta = (4098 * es) / ((temp + 237.3) ** 2)

                G = 0  # soil heat flux

                numerator = 0.408 * delta * (Rn - G) + gamma * (37 / (temp + 273)) * wind_m_s * (es - ea)
                denominator = delta + gamma * (1 + 0.34 * wind_m_s)

                et_hour = numerator / denominator
                total_et += et_hour if et_hour > 0 else 0  # avoid negatives
            except:
                continue  # skip faulty hour

        return round(total_et, 4)  # mm/day
