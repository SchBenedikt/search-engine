import requests
import datetime
from typing import Dict, Optional, Any


class WeatherService:
    """Service to get weather information without requiring an API key"""
    
    def __init__(self):
        self.base_url = "https://wttr.in"
    
    def get_weather(self, location: str) -> Optional[Dict[str, Any]]:
        """
        Get weather information for a location
        
        Args:
            location: The location to get weather for
            
        Returns:
            Dictionary containing weather information or None if not found
        """
        try:
            # Format the location query for the URL
            formatted_location = location.replace(" ", "+")
            
            # Get basic weather data in JSON format - force English language
            response = requests.get(
                f"{self.base_url}/{formatted_location}?format=j1&lang=en",
                headers={"User-Agent": "Mozilla/5.0"}
            )
            
            if response.status_code != 200:
                return None
                
            data = response.json()
            
            # Process the data to create our weather panel
            current_condition = data.get("current_condition", [{}])[0]
            weather_desc = current_condition.get("weatherDesc", [{}])[0].get("value", "Unknown")
            temp_c = current_condition.get("temp_C", "N/A")
            temp_f = current_condition.get("temp_F", "N/A")
            feels_like_c = current_condition.get("FeelsLikeC", "N/A")
            feels_like_f = current_condition.get("FeelsLikeF", "N/A")
            humidity = current_condition.get("humidity", "N/A")
            wind_speed = current_condition.get("windspeedKmph", "N/A")
            wind_dir = current_condition.get("winddir16Point", "N/A")
            
            # Get forecast data
            forecast = []
            for day in data.get("weather", [])[:3]:  # Get forecast for up to 3 days
                date = day.get("date", "")
                max_temp_c = day.get("maxtempC", "N/A")
                min_temp_c = day.get("mintempC", "N/A")
                
                # Format date
                try:
                    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")
                    formatted_date = date_obj.strftime("%a, %d %b")  # e.g. "Mon, 17 Apr"
                except:
                    formatted_date = date
                
                # Get the weather description from the first hourly entry
                hourly = day.get("hourly", [{}])[0]
                day_weather_desc = hourly.get("weatherDesc", [{}])[0].get("value", "Unknown")
                
                forecast.append({
                    "date": formatted_date,
                    "max_temp_c": max_temp_c,
                    "min_temp_c": min_temp_c,
                    "weather_desc": day_weather_desc,
                    "weather_icon": hourly.get("weatherIconUrl", [{}])[0].get("value", "")
                })
            
            # Get location details
            area_name = data.get("nearest_area", [{}])[0].get("areaName", [{}])[0].get("value", "Unknown")
            region = data.get("nearest_area", [{}])[0].get("region", [{}])[0].get("value", "")
            country = data.get("nearest_area", [{}])[0].get("country", [{}])[0].get("value", "")
            
            # Create the weather panel data
            weather_panel = {
                "location": {
                    "name": area_name,
                    "region": region,
                    "country": country,
                    "full_name": ", ".join(filter(None, [area_name, region, country]))
                },
                "current": {
                    "temp_c": temp_c,
                    "temp_f": temp_f,
                    "feels_like_c": feels_like_c,
                    "feels_like_f": feels_like_f,
                    "weather_desc": weather_desc,
                    "humidity": humidity,
                    "wind_speed": wind_speed,
                    "wind_dir": wind_dir,
                    "weather_icon": current_condition.get("weatherIconUrl", [{}])[0].get("value", "")
                },
                "forecast": forecast,
                "updated": datetime.datetime.now().strftime("%H:%M, %d %b %Y")
            }
            
            return weather_panel
            
        except Exception as e:
            print(f"Error fetching weather data: {e}")
            return None
    
    def is_weather_query(self, query: str) -> bool:
        """
        Check if a query is likely to be a weather query
        
        Args:
            query: The search query
            
        Returns:
            True if it's likely a weather query, False otherwise
        """
        weather_keywords = [
            "weather", "wetter", "tiempo", "météo", "meteo", 
            "forecast", "temperature", "temperatur", "temperatura",
            "rain", "regen", "lluvia", "pluie",
            "snow", "schnee", "nieve", "neige",
            "humidity", "feuchtigkeit", "humedad", "humidité",
            "sunny", "sonnig", "soleado", "ensoleillé",
            "cloudy", "bewölkt", "nublado", "nuageux",
            "climate", "klima", "clima", "climat"
        ]
        
        # Check for common patterns like "weather in X" or "X weather"
        query_lower = query.lower()
        
        # Check if the query contains a weather keyword
        for keyword in weather_keywords:
            if keyword in query_lower:
                return True
        
        # Check for patterns like "weather in X" or "X weather"
        if ("weather in" in query_lower or 
            "wetter in" in query_lower or 
            "tiempo en" in query_lower or 
            "météo à" in query_lower or
            query_lower.endswith(" weather") or
            query_lower.endswith(" wetter") or
            query_lower.endswith(" tiempo") or
            query_lower.endswith(" météo")):
            return True
            
        return False
        
    def extract_location(self, query: str) -> str:
        """
        Extract the location from a weather query
        
        Args:
            query: The search query
            
        Returns:
            The extracted location or empty string if not found
        """
        query_lower = query.lower()
        
        # Try to extract location from patterns like "weather in X"
        patterns = [
            "weather in ", "wetter in ", "tiempo en ", "météo à ", 
            "forecast for ", "weather forecast for ", "temperature in ",
            "temperatur in ", "temperatura en ", "température à "
        ]
        
        for pattern in patterns:
            if pattern in query_lower:
                return query[query_lower.index(pattern) + len(pattern):].strip()
        
        # Try to extract location from patterns like "X weather"
        patterns_suffix = [
            " weather", " wetter", " tiempo", " météo",
            " forecast", " temperature", " temperatur", " temperatura"
        ]
        
        for pattern in patterns_suffix:
            if query_lower.endswith(pattern):
                return query[:len(query) - len(pattern)].strip()
        
        # If no pattern matched, just return the query with weather-related words removed
        weather_terms = [
            "weather", "wetter", "tiempo", "météo", "meteo", 
            "forecast", "temperature", "temperatur", "temperatura",
            "rain", "regen", "lluvia", "pluie",
            "snow", "schnee", "nieve", "neige",
            "humidity", "feuchtigkeit", "humedad", "humidité",
            "sunny", "sonnig", "soleado", "ensoleillé",
            "cloudy", "bewölkt", "nublado", "nuageux", 
            "climate", "klima", "clima", "climat"
        ]
        
        cleaned_query = query_lower
        for term in weather_terms:
            cleaned_query = cleaned_query.replace(term, "")
        
        # Clean up any remaining extra spaces and punctuation
        cleaned_query = " ".join(cleaned_query.split())
        cleaned_query = cleaned_query.strip(" ,.;:-?!")
        
        return cleaned_query or query  # Return original query if cleaned query is empty
