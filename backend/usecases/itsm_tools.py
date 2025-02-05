from langchain.agents import tool
import requests
from requests.auth import HTTPBasicAuth

# Define the ServiceNow instance details
instance = "dev285368"
username = "admin"
password = "iq9E^2ka+HZH"


@tool
def create_incident(short_description: str, description: str) -> str:
    """
    Creates an incident in ServiceNow and returns the incident number.
    
    Args:
        short_description (str): A brief description of the incident.
        description (str): A detailed description of the incident.
        
    Returns:
        str: The incident number if the incident was created successfully.
    """
    # ServiceNow API endpoint
    url = f"https://{instance}.service-now.com/api/now/table/incident"

    # Incident data
    payload = {
        "short_description": short_description,
        "description": description
    }

    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Make the API request
    response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 201:
        incident_number = response.json().get("result").get("number")
        return f"Incident created successfully. Incident Number: {incident_number}"
    else:
        return f"Failed to create incident. Status code: {response.status_code}. Response: {response.json()}"


@tool
def add_user(email: str) -> str:
    """
    Adds a user to ServiceNow using the provided email.
    
    Args:
        email (str): The user's email address.
        
    Returns:
        str: The user sys_id if the user was added successfully, or an error message.
    """
    # Extract first name, last name, and user ID from email
    if '@' not in email:
        return "Invalid email format."

    user_id = email.split('@')[0]
    name_parts = user_id.split('.')
    
    if len(name_parts) != 2:
        return "Unable to extract first and last name from email."

    first_name, last_name = name_parts[0].capitalize(), name_parts[1].capitalize()

    # ServiceNow API endpoint for creating a new user
    url = f"https://{instance}.service-now.com/api/now/table/sys_user"

    # User data payload
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "user_name": user_id
    }

    # Headers
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # Make the API request to create the user
    response = requests.post(url, auth=HTTPBasicAuth(username, password), headers=headers, json=payload)

    # Check if the request was successful
    if response.status_code == 201:
        user_sys_id = response.json().get("result").get("sys_id")
        return f"User added successfully. User sys_id: {user_sys_id}"
    else:
        return f"Failed to add user. Status code: {response.status_code}. Response: {response.json()}"


from google.cloud import compute_v1

@tool
def restart_instance(instance_name: str) -> str:
    """
    Restarts a server in Google cloud
    
    Args:
        instance_name (str): Name of the GCP instance.
        
    Returns:
        str: message If the the instances is started 
    """
    project_id = "personal-411514"
    zone = "us-central1-c"
    #instance_name = "hnk-db"
    # Create a client for the Compute Engine API
    instance_client = compute_v1.InstancesClient()

    # Get the current status of the instance
    instance = instance_client.get(project=project_id, zone=zone, instance=instance_name)
    if instance.status == "TERMINATED":
        print(f"The instance {instance_name} is already stopped. Starting the instance.")
        operation = instance_client.start(project=project_id, zone=zone, instance=instance_name)
    else:
        print(f"Restarting the instance {instance_name}.")
        # Restart the instance by stopping and starting it
        stop_operation = instance_client.stop(project=project_id, zone=zone, instance=instance_name)
        stop_operation.result()  # Wait for the operation to complete
        operation = instance_client.start(project=project_id, zone=zone, instance=instance_name)

    operation.result()  # Wait for the operation to complete
    return(f"Instance {instance_name} has been restarted.")