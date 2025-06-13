import datetime

def get_current_time(params: dict) -> str: # Added params
    """
    Retrieves the current time and formats it into a user-friendly string.
    Params is unused but included for consistent skill signature.
    """
    now = datetime.datetime.now()
    formatted_time = now.strftime("%I:%M %p")
    return f"The current time is {formatted_time}."

def open_application(params: dict) -> str: # Updated signature
    """
    Conceptually attempts to open an application.
    For now, it just returns a message indicating the attempt.
    """
    app_name = params.get('appName')
    if not app_name:
        return "No application name specified for opening."
    return f"Attempting to open {app_name}..."

def search_web(params: dict) -> str:
    """
    Placeholder skill for searching the web.
    """
    query = params.get('query', 'anything specific') # Default if query somehow not provided
    return f"I would now search the web for: '{query}'."

def check_weather_skill(params: dict) -> str:
    """
    Placeholder skill for checking the weather.
    Params is unused for now but could take location in future.
    """
    return "Fetching the latest weather forecast for you."

SKILL_REGISTRY = {
    "getTime": get_current_time,
    "openApp": open_application,
    "searchWeb": search_web,
    "checkWeather": check_weather_skill,
}
