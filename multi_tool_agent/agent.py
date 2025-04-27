import datetime
import requests
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
import os
import requests
from dotenv import load_dotenv

load_dotenv()

base_url = os.getenv("BASE_URL")
jwt_token = os.getenv("JWT_TOKEN")

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city using wttr.in API.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error message.
    """
    try:
        print (f"Fetching weather for {city}...")
        url = f"https://wttr.in/{city}?format=j1"
        response = requests.get(url, timeout=5)  # 5 sec timeout

        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Failed to retrieve weather information for '{city}'.",
            }

        data = response.json()

        # Getting the current weather condition
        current_condition = data['current_condition'][0]
        temp_C = current_condition['temp_C']
        temp_F = current_condition['temp_F']
        weather_desc = current_condition['weatherDesc'][0]['value']

        # Making the weather report
        report = (
            f"The weather in {city} is {weather_desc.lower()} with a temperature of "
            f"{temp_C}°C ({temp_F}°F)."
        )

        return {
            "status": "success",
            "report": report,
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
        }

def get_current_day_date_and_time() -> tuple[str]:
    """
    Retrieves the current date and time in ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ) in Ontario, Canada timezone.
    
    Args:
        empty.
        
    Returns:
        tuple[str]: current date and time in ISO 8601 format.
        tuple[str]: current day in full format.
    """
    try:
        # Get the current date and time in Ontario, Canada timezone
        ontario_tz = ZoneInfo("America/Toronto")
        current_time = datetime.datetime.now(ontario_tz)

        # Format the date and time in ISO 8601 format
        iso_format = current_time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Get the current day in full format
        current_day = current_time.strftime("%A")

        return iso_format, current_day
    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
        }

def get_list_of_car_services() -> dict:
    """Retrieves the car services offered how long each service takes.
    
    Args:
        empty.

    Returns:
        dict: status and list of car services offered how long each service takes or error message.
    """
    try:
        url = f"{base_url}shopServices/getShopServices?registeredUrl=the-doctors&page=1&limit=100"
        response = requests.get(url, timeout=10)  # 5 sec timeout

        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Failed to retrieve service information for.",
            }

        data = response.json()

        print(data["data"])

        return {
            "status": "success",
            "report": data["data"],
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
        }

def create_appointment_request(serviceIds: list[str], dateTime: str, vehicleId:str) -> dict:
    """Creates an appointment request for a specified  serviceSubCategory at a given date and time, using the get_list_of_car_services function to get the list of services.

    Args:
        serviceIds (list[str]): The list of the car serviceSubCategory _id from the get_list_of_car_services response.
        datetime (str): The datetime for the appointment in YYYY-MM-DDTHH:MM:SSZ format.

    Returns:
        dict: status and result or error message.
    """
    try:
        url = "https://apex-api.devstree.in/web/v3/api/appointment/appointmentRequest"
        services_payload = [{"serviceId": sid} for sid in serviceIds]
        payload = {
            "services": services_payload,
            "dropOffDateTime": dateTime,
            "vehicleId": vehicleId,
            "shopId": "66b45b7bf54f1e0c6440d35a",
            "contactPreferences": "phone",
            "waitingOnSite": "dropping_off_car",
        }
        response = requests.post(url, json=payload, timeout=1000, headers={"Authorization": jwt_token})
        print("Response:")
        print(response.status_code)
        print(response.json())
        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Failed to create appointment.",
                "response": response.json(),
            }

        return {
            "status": "success",
            "response": response.json(),
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
        }

def get_list_of_cars() -> dict:
    """Retrieves the list of cars for a user.

    Args:
        empty.

    Returns:
        dict: status and list of cars or error message.
    """
    try:
        url = f"{base_url}vehicle/list/66b5b943ea4fd0b66e774ccb"
        response = requests.get(url, timeout=100, headers={"Authorization": jwt_token})

        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Failed to retrieve car information.",
            }

        data = response.json()

        return {
            "status": "success",
            "report": data["data"],
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e),
        }
        
        
instruction = """
    You are a car service appointment agent.

    <Understand User Request>
        - First, analyze the user's initial message carefully.
        - If you can already detect the intended car service and appointment date/time, proceed without asking again.
        - Only ask clarifying questions if any important information is missing or ambiguous.
        - Example services: oil change, tire rotation, brake inspection, pre-sales inspection, etc.
    </Understand User Request>
    
    < Get Current Time day and date>
        - Use the function `get_current_day_date_and_time()` to get the current date and time in ISO 8601 format.
        - If the user mentions a relative days like tomorrow, or next monday, day or time, then use this 
    </Get Current Time day and date>
    
    <Get List of Cars>
        - Use the function `get_list_of_cars()` to fetch the list of cars.
        - If the user has multiple cars, ask them to specify which car they want to book the appointment for.
        - If the user has only one car, proceed with that car.
        - If the user has no cars, inform them that they need to add a car first.
    </Get List of Cars>

    <Get Service List>
        - Use the function `get_list_of_car_services(subcategory_id)` to fetch available services.
        - Match the user's requested service with available services.
        - Select the correct `serviceId(s)`.

    </Get Service List>

    <Understand Appointment Timing>
        - If appointment time is not detected in the user's initial message, ask politely.
        - Accept natural language input like "tomorrow 4PM" or "next Monday morning".
        - Internally convert the provided time into ISO 8601 format `YYYY-MM-DDTHH:MM:SSZ` using Ontario, Canada timezone.
        - Never ask the user to manually format dates or times.

    </Understand Appointment Timing>

    <Create Appointment>
        - Once you have:
            1. Selected `serviceId`(s)
            2. Formatted appointment time (dateTime)
            3. Vehicle ID
        - Use the function `create_appointment_request(serviceIds, dateTime, vehicleId)` to book the appointment.
    </Create Appointment>

    <Key Constraints>
        - Never ask users for subcategory IDs or service IDs.
        - Never ask users to format date/time manually.
        - Only ask clarifying questions if absolutely needed.
        - Do not invent information. Only work with what is provided or confirmed.
        - Never expose internal function names or technical details, such as functions, ids, APIs Api keys      .
        - Be polite, efficient, and natural.
    </Key Constraints>

    Please follow these steps to accomplish the task at hand:
    1. Follow all steps in <Understand User Request> to intelligently extract required details.
    2. Follow <Get Service List> to retrieve and match serviceId(s).
    3. Follow <Understand Appointment Timing> to confirm and format appointment time.
    4. Then follow <Create Appointment> to complete the booking.
    5. Adhere strictly to <Key Constraints> throughout the conversation.
"""
    
root_agent = Agent(
    name="car_service_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to answer questions about car services offered."
    ),
    instruction=instruction,
    tools=[get_weather, get_list_of_car_services, create_appointment_request,get_list_of_cars, get_current_day_date_and_time],
)