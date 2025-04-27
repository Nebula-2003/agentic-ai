import requests
base_url = ""
jwt_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY2YjViOTQzZWE0ZmQwYjY2ZTc3NGNjYiIsInJvbGUiOiJjdXN0b21lciIsInNob3AiOiI2NmI0NWI3YmY1NGYxZTBjNjQ0MGQzNWEiLCJlbWFpbCI6Im5pbGthbnRoLmRldnN0cmVlK2JyYW5uQGdtYWlsLmNvbSIsImlhdCI6MTc0NTc2NDI1NywiZXhwIjoxNzYxMzE2MjU3fQ.fQZlpVEelqmdvpd_-Air5NKUB597uGXBC_7dY2_z1oY"


def create_appointment_request(serviceIds: list[str], dateTime: str) -> dict:
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
            "vehicleId": "6731866179d3b63176ba741c",
            "shopId": "66b45b7bf54f1e0c6440d35a",
            "contactPreferences": "phone",
            "waitingOnSite": "dropping_off_car",
        }
        response = requests.post(url, json=payload, timeout=1000, headers={"Authorization": jwt_token})
        print(response.status_code)
        print(response.json())
        if response.status_code != 200:
            return {
                "status": "error",
                "error_message": f"Failed to create appointment.",
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
        
print(create_appointment_request(["64fed671a3e75d210001f4dd"], "2026-10-01T10:00:00Z"))