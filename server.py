import random
import requests
import json

from fastmcp import FastMCP
from fastapi.responses import JSONResponse
from pinecone import Pinecone
from pydantic import BaseModel
from langchain.tools import tool
from typing import Dict
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, base_url


# Initialize Pinecone client
pinecone = Pinecone(api_key=PINECONE_API_KEY)
index = pinecone.Index(PINECONE_INDEX_NAME)

mcp = FastMCP(name="evaaServer")





@mcp.tool()
def roll_dice(n_dice: int) -> list[int]:
    """Roll `n_dice` 6-sided dice and return the results."""
    return [random.randint(1, 6) for _ in range(n_dice)]





# Initialize Pinecone client
pinecone = Pinecone(api_key=PINECONE_API_KEY)
index = pinecone.Index(PINECONE_INDEX_NAME)


@mcp.tool()
def rag_retrieval_tool(query: str) -> str:
    """
    Use This tool to retrieves relevant information from the vector store based on the user's query.
    """
    try:
        ranked_results = index.search_records(
            namespace="hr4s", 
            # namespace="mark1", 
            query={
                "inputs": {"text": query},
                "top_k": 7
            },
            rerank={
                "model": "bge-reranker-v2-m3",
                "top_n": 5,
                "rank_fields": ["text"]
            },
            # fields=["category", "text"]
        )

        results = ranked_results.result.hits
        if not results:
            return "Sorry, I couldn't find any relevant information."
        
        return f"Here’s what I found:\n\n{results}"

    except Exception as e:
        return f"Error retrieving context from Pinecone: {e}"






def get_welcomeform_token(practice) -> str:
    """
        Get authentication token using vendor and account credentials.
    """
    print("Get practice authentication token")
    auth_url = f"{base_url}Authenticate"

    auth_payload = None
    
    credentials = {
    "burneteyecarepinecone": [
        {
            "vendorName": "MaximEyesIO",
            "accountId": "burneteyecarepinecone",
            "vendorId": "e59ec838-2fc5-4639-b761-78e3ec55176c",
            "vendorPassword": "password@123",
            "accountPassword": "UDUA7978@707"
        },
        {
            "vendorName": "Chatbot",
            "accountId": "burneteyecarepinecone",
            "vendorId": "e59ec838-2fc5-4639-b761-78e3ec55187b",
            "vendorPassword": "MrklIuaJzKbzlMSNKamZppiLvSrL4hgdjFGoO9iEPo0=",
            "accountPassword": "2OGlud/kNcFyJ7kZEfVMpdfDx+0v4+btATgsp2LgZ6E="
        },
        {
            "vendorName": "WelcomeformAPI",
            "accountId": "burneteyecarepinecone",
            "vendorId": "e544cb04-305e-4488-aaaa-2978a2b83e0f",
            "vendorPassword": "password@123",
            "accountPassword": ""
        },
        {
            "vendorName": "Python Dumping",
            "accountId": "burneteyecarepinecone",
            "vendorId": "f6644ae4-d2f9-474b-b8b6-ebe8c3c9b322",
            "vendorPassword": "password@123",
            "accountPassword": ""
        }
    ]
}

    
    print(f"Heres dictionary with required data : {credentials}")
    for val in credentials[f'{practice}']:
        if val["vendorName"] == "WelcomeformAPI":
            auth_payload = val
        
    headers = {'Content-Type': 'application/json'}
    try:
        auth_response = requests.post(auth_url, json=auth_payload, headers=headers)
        auth_response.raise_for_status()
        # response_json = auth_response.json()
        response_text = auth_response.text
        return response_text

    except requests.RequestException as e:
        return f"Authentication failed: {str(e)}"
    except json.JSONDecodeError:
        return "Failed to decode JSON response" 



def get_customer_id_from_details(first_name, last_name, dob, phone_number,session_id):    
    print('Inside get_customer_id_from_details function')
    
    middle_name = ''
    email = ''

    path = "e1/burneteyecarepinecone/QApixW"
    practice = path.split('/')[-2]
    
    token = get_welcomeform_token(practice)

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'bearer {token}'
    }
    
    payload = {
        "firstName": first_name,
        "lastName": last_name,
        "middleName": middle_name,
        "dob": dob,
        "phoneNumber": phone_number,
        "email": email,
        "SessionID": session_id
    }
    
    print('CB_GetCustomerIdFromDetails request is: %s', json.dumps(payload))

    url = f"{base_url}api/Home/CB_GetCustomerIdFromDetails"
    #url = "https://welcomeformchatbotapi.maximeyes.com/api/Home/CB_GetCustomerIdFromDetails"
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        try:
            response_data = response.json()
            # assigning customerId here
            # customer_id = response_data.customerId;
            customer_id = response_data.get('customerId')
            print(f"Response data for ID here ::: {response_data}")
            
        except ValueError:
            return JSONResponse({"error": "Failed to parse JSON response."}, status=500)
        return response_data
    except requests.exceptions.RequestException as e:
        print(f"API call failed: {e}")
        return JSONResponse({"error": f"Failed to connect to API: {str(e)}"}, status=500)
    


@mcp.tool()
def get_patient_appointment_status(
    first_name: str,
    last_name: str,
    dob: str,
    phone_number: str
) -> dict:
    """ 
    Use this function to check your appointment status.
    Check your appointment status from their information such as first_name, last_name, db and phone_number
    """
    print(f"Inside appt status tool...")
    try:
        path = "e1/burneteyecarepinecone/QApixW"
        practice = path.split('/')[-2]

        session_id = '563a8ea9-d417-4ee6-941c-78c16759c088'
        
        print(f"Session ID here from patient appt status ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {session_id}")   
        print(f"Session ID here from patient appt status ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {session_id}")   
        print(f"Session ID here f5rom patient appt status ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::: {session_id}") 

        # Assuming get_welcomeform_token() is defined somewhere
        token = get_welcomeform_token(practice)
        
    except Exception as e:
        print(f"Error fetching the practice or token: {e}")
        all_appointments_str = "User Not Found, Failed to get appointment."
        return JSONResponse({"response": all_appointments_str})

    # change here for patient id2 
    # patient_id = data.get('patient_id', '')
    ids = get_customer_id_from_details(first_name, last_name, dob, phone_number,session_id)
    patient_id = ids.get('patientNumber')
    print(f"Go find your patient id in this :: {patient_id}")
    
    if not patient_id:
        all_appointments_str = "User Not Found, Failed to get appointment."
        return JSONResponse({"response": all_appointments_str})

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }

    # The URL to get the appointment details
    get_appointment_url = f"{base_url}api/Appointment/CB_getAppointment?patientNumber={patient_id}"
    #get_appointment_url = f"https://welcomeformchatbotapi.maximeyes.com/api/Appointment/CB_getAppointment?patientNumber={patient_id}"

    try:
        response = requests.get(get_appointment_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"An error occurred in API call to get appointment: {e}")
        return JSONResponse({"error": "Failed to get appointment."}, status=500)

    # Check if response status is 200 (OK)
    if response.status_code == 200:
        response_data = response.json()
        print(f"Response data from get_appointments: {response_data}")

        # Now, format the appointments into a structured message
        formatted_appointments = []
        
        for appointment in response_data:
            appointment_details = (
                f"Reason: {appointment.get('reasonName', 'N/A')}, "
                f"Location: {appointment.get('locationName', 'N/A')}, "
                f"Provider: {appointment.get('resourceName', 'N/A')}, "
                f"Date: {appointment.get('start', 'N/A').split('T')[0]}, "  # Extract date from datetime
                f"Time: {appointment.get('start', 'N/A').split('T')[1]}, "  # Extract time from datetime
                f"Appointment Status: {appointment.get('appointmentStatus', 'N/A')}"
            )
            
            formatted_appointments.append(appointment_details)
        
        header = f"Your Appointment Status is here : \nName: {first_name} {last_name}\n\n"
        all_appointments_str = header + "\n".join(formatted_appointments)
        print(f"Response from the patient appt status here :::::::::::: {all_appointments_str}")

                
        # If appointments exist, return them
        if formatted_appointments:
            return all_appointments_str
        else:
            return JSONResponse({"response": "No appointments found for the patient."})
    
    else:
        return JSONResponse({"response": "Failed to get appointment. User might not exist."}, status=500)








if __name__ == "__main__":
    # mcp.run(transport="sse", port=8005)
    # mcp.run(transport="stdio")
    mcp.run(transport="streamable-http")



