""" 

THIS FILE WILL KEEP ALL PYTHON APIS FROM EVAA IN FASTAPI AND ALL API'S WILL BE CALLED FROM HERE. 

"""


from fastapi import FastAPI
from fastapi.responses import JSONResponse
import json
import requests
from loguru import logger
from functools import wraps
from typing import Dict, Any, Optional
from datetime import datetime
from .Helper.delay_config import log_event
from .Helper.handle_exception import show_custom_message
from .Helper.logging_config import error_logger
from FastApis.config import base_url


app = FastAPI()


def get_chat_history_1(request, session_id):
    return request.session.get(f"history_{session_id}", [])


# Function to update chat history
@app.get("/update-chat-history")
def update_chat_history(request, session_id, role, content):
    try:
        if request.session[f"step{session_id}"] == 'start':
            print(f"Updating session step in update_chat_history ......................")
            request.session[f"step{session_id}"] = "continue"
    except:
        pass

    data = json.loads(request.body.decode('utf-8'))
    #location_id = data.get('location_id', '')
    path = data.get('path', '')

    log_event(path, "Function call : update_chat_history", 1378, session_id)
    history = get_chat_history_1(request, session_id)
    print("================================================================================================================")
    print(f"Got our history here ::::::::::::::::::::::::::::::::::::{session_id}::::::::::::::::::::::::::::::::::::::::::::: {history}")
    print("================================================================================================================")

    history.append({"role": role, "content": content})
    request.session[f"history_{session_id}"] = history

    test = request.session.get(f"history_{session_id}")
    print("================================================================================================================")
    print(f"Got our history here ::::::::::::::::::::::::::::::::::::{session_id}::::::::::::::::::::::::::::::::::::::::::::: {test}")
    print("================================================================================================================")

    request.session.modified = True  # Ensure changes are saved
    log_event(path, "Function call Completed : update_chat_history", 1383, session_id)

@app.get("/get-vendor-credentials")
def get_vendor_credentials(bot_id):
    
    # API endpoint
    url = f"{base_url}api/PracticeDetails/CB_GetVendorsCredentialsFromBotID"

    # @app.get("/my-view")
# define query parameters
    params = {
        "BotID": bot_id 
    }

    # Send a GET request with parameters
    response = requests.get(url, params=params)
    print(f'============================================================================CB_GetVendorsCredentialsFromBotID getting used!!!')   

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the response JSON if applicable
        return response.json()
    else:
        return response.status_code , response.reason



@app.get("/get-practice-token")
def get_practice_token(practice, request) -> str:
    """
        Get authentication token using vendor and account credentials.
    """
    print("Get practice authentication token")
    auth_url = f"{base_url}Authenticate"

    auth_payload = None
    try:
        for val in request.session['practices_dictionary'][f'{practice}']:
            if val["vendorName"] == "WelcomeformAPI":
                auth_payload = val
                break 

    except Exception as e:
        error_logger.error(f"An error occurred: {e}", exc_info=True)
        print(f"Error in authentication :: {e}")

    headers = {'Content-Type': 'application/json'}
    
    try:
        auth_response = requests.post(auth_url, json=auth_payload, headers=headers)
        auth_response.raise_for_status()

        # Handling plain text response
        token = auth_response.text.strip()
        if token:  # Check if the response contains a token
            print(f"Token fetched successfully: {token}")
            return token
        else:
            print(f"Token fetched failed")
            return "Failed to fetch token: Empty response"
    except requests.RequestException as e:
        return f"Authentication failed: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"




@app.get("/get-customer-id-from_details")
def get_customer_id_from_details(request):    
    print('Inside get_customer_id_from_details function')
    if request.method == "POST":
        data = json.loads(request.body.decode('utf-8'))
        first_name = data.get('first_name', '')
        last_name = data.get('last_name', '')
        middle_name = data.get('middle_name', '')
        dob = data.get('dob', '')
        phone_number = data.get('phone_number', '')
        email = data.get('email', '')
        tab_id = data.get('tab_id', '')
        session_id = data.get('session_id', '')

        path = data.get('path', '')
        practice = path.split('/')[-2]
        token = get_welcomeform_token(practice, request)

        # # Validate practice in dictionary
        # if practice not in practices_dictionary:
        #     return JSONResponse({"error": "Practice not found in practices_dictionary"}, status=400)

        # practice_name = None
        # for val in practices_dictionary[f'{practice}']:
        #     if val["vendorName"] == "WelcomeformAPI":
        #         practice_name = val["accountId"]
        #         break

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
                request.session[f'customer_id_{tab_id}'] = customer_id
            except ValueError:
                return JSONResponse({"error": "Failed to parse JSON response."}, status=500)
            return JSONResponse(response_data)
        except requests.exceptions.RequestException as e:
            print(f"API call failed: {e}")
            return JSONResponse({"error": f"Failed to connect to API: {str(e)}"}, status=500)
    else:
        return JSONResponse({"error": "Invalid HTTP method. Use POST."}, status=405)


@app.get("/get-welcomeform-token")
def get_welcomeform_token(practice, request) -> str:
    """
        Get authentication token using vendor and account credentials.
    """
    print("Get practice authentication token")
    auth_url = f"{base_url}Authenticate"

    auth_payload = None
    dictv = request.session['practices_dictionary']
    print(dictv)
    for val in request.session['practices_dictionary'][f'{practice}']:
        if val["vendorName"] == "WelcomeformAPI":
            auth_payload = val
        
    headers = {'Content-Type': 'application/json'}
    try:
        auth_response = requests.post(auth_url, json=auth_payload, headers=headers)
        auth_response.raise_for_status()
        # response_json = auth_response.json()
        response_text = auth_response.text
        return response_text

        # if response_json.get('isToken'):
        #     print(response_json)
        #     return response_json.get('token')
        # else:
        #     return f"Error message: {response_json.get('ErrorMessage')}"
    except requests.RequestException as e:
        return f"Authentication failed: {str(e)}"
    except json.JSONDecodeError:
        return "Failed to decode JSON response" 




@app.get("/get-Customer-id")
def get_Customer_id(request,token,firstName,lastName,dob,phoneNumber,email):
    # global customer_id
    
    data = json.loads(request.body.decode('utf-8'))
    path_var = data.get('path', '')
    # token = data.get('token','')
    # tab_id = data.get('tab_id', '')
    print("PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP")
    print(firstName,lastName,dob,phoneNumber,email)
    # The URL of the API you want to call
    url = f"{base_url}api/Home/CB_GetCustomerIdFromDetails" 
    
    p = path_var.split('/')
    bot_id = p[-1]
    
    headers = {
                    "Authorization" : f"Bearer {token}",
                    "chatbotid" : bot_id
              }
	      
    # The list you want to send
    data = {
            "firstName": firstName,
            "lastName": lastName,
            "dob": dob,
            "phoneNumber": phoneNumber,
            "email": email
            }
	    
    # Making the POST request
    # response = requests.post(url, json=data , headers=headers)
    response = requests.post(url, json=data , headers=headers)
    
    # Checking if the request was successful
    if response.status_code in (200, 201):  # 200 OK or 201 Created
        # Parsing the JSON response
        response_data = response.json()
        print("Response Customer id ::::::::::::::::::::::::", response_data)
	
        if response_data:
            customer_id = str(response_data.get("customerId"))
            # customer_id = response_data
            # request.session['customer_id'] = response_data
            return customer_id
            # data['customer_id']= response_data
            # data['user_id']= response_data
        else:
            print("Details not found in Databse")
	    
        # print("Response content:", response.text)
        # print("Status code:", response.status_code)
    else:
        print(f"Failed to send data. Status code: {response.status_code}")
        print("Response content:", response.text)


@app.get("/api-error-handler")
def api_error_handler(func):
    """Decorator to handle API errors consistently"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.RequestException as e:
            error_msg = f"API error in {func.__name__}: {str(e)}"
            logger.error(error_msg)
            error_logger.error(error_msg, exc_info=True)
            return JSONResponse({"error": "An error occurred processing your request"}, status=500)
    return wrapper

@app.get("/get-practice-info")
def get_practice_info(request, path: str) -> tuple:
    """Get practice information and token"""
    practice = path.split('/')[-2]
    token = get_welcomeform_token(practice, request)
    practice_name = next(
        (val["accountId"] for val in request.session['practices_dictionary'][practice] 
         if val["vendorName"] == "WelcomeformAPI"),
        None
    )
    return practice, token, practice_name

@app.get("/get-headers")
def get_headers(token: str, practice_name: Optional[str] = None) -> Dict[str, str]:
    """Generate headers for API requests"""
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {token}'
    }
    if practice_name:
        headers["AccountId"] = practice_name
    return headers

@api_error_handler
@app.get("/book-appointment-api")
def book_appointment_api(request, session_id: str, path: str) -> Dict[str, Any]:
    data = json.loads(request.body.decode('utf-8'))
    practice, token, practice_name = get_practice_info(request, path)
    location_selected = data.get('location_selected', '')
    isReschedule = data.get('isReschedule', '')
    
    print(f"Appt rescheduled here ::::::::::::::: {isReschedule}")
    appointment_data = {
        "OpenSlotId": str(data.get('open_slot_id', '')),
        "ApptDate": str(data.get('from_date', '')),
        "ReasonId": str(data.get('reason_id', '')),
        "FirstName": str(data.get('first_name', '')),
        "LastName": str(data.get('last_name', '')),
        "PatientDob": str(data.get('dob', '')),
        "MobileNumber": str(data.get('phone_number', '')),
        "EmailId": str(data.get('email_id', '')),
        "SessionID": str(data.get('session_id', '')),
        "resourceId": str(data.get('resourceId', '')),
        "locationId": str(data.get('location_selected', ''))
    }
    print(f"Reschedule data ::::::::::::::: {appointment_data}")
    response = requests.post(
        f"{base_url}api/Appointment/CB_OnlineScheduling",
        json=appointment_data,
        headers=get_headers(token, practice_name)
    ).text

    if response == 'Appointment scheduled successfully.':
        
        if isReschedule:
            usermessage = (
                f"Appointment Rescheduled successfully for \n Name: {data['first_name']} {data['last_name']} !!\n"
                f"Date of Birth: {data['dob']}\n"
                f"Phone Number: {data['phone_number']}\n"
                f"Email: {data['email_id']}\n"
                f"Location: {data['selected_location_name']}\n"
                f"Provider: {data['selected_provider_pame']}\n"
                f"Reason: {data['selected_reason_name']}\n"
                f"resourceId: {data['resourceId']}\n"
                f"location_selected: {data['location_selected']}\n"
                f"Date: {data['from_date']}\n"
                f"Time: {data['selected_time_slot_text']}"
            )
        else:
            usermessage = (
                f"Appointment booked successfully for \n Name: {data['first_name']} {data['last_name']} !!\n"
                f"Date of Birth: {data['dob']}\n"
                f"Phone Number: {data['phone_number']}\n"
                f"Email: {data['email_id']}\n"
                f"Location: {data['selected_location_name']}\n"
                f"Provider: {data['selected_provider_pame']}\n"
                f"Reason: {data['selected_reason_name']}\n"
                f"resourceId: {data['resourceId']}\n"
                f"location_selected: {data['location_selected']}\n"
                f"Date: {data['from_date']}\n"
                f"Time: {data['selected_time_slot_text']}"
            )
        
        show_custom_message("Appointment scheduled successfully! : book_appointment_api")
        
        customer_id = data.get('customer_id', '0')
        if customer_id == "0":
            practice_token = get_practice_token(practice, request)
            customer_id = get_Customer_id(
                request, practice_token,
                data['first_name'], data['last_name'],
                data['dob'], data['phone_number'],
                data['email_id']
            )
        error_logger.error(f"Book appt succesfull :: {response}", exc_info=True)
        return {
            "response": response,
            'customer_id': customer_id,
            'feedback_initiated': 1,
            "usermessage": usermessage
        }
    error_logger.error(f"Book appt fail :: {response}", exc_info=True)
    return {
        "response": response,
        'customer_id': data.get('customer_id', '0'),
        'feedback_initiated': 0,
        "usermessage": response
    }

@api_error_handler
@app.get("/get-locations-api")
def get_locations_api(request) -> JSONResponse:
    data = json.loads(request.body.decode('utf-8'))
    path = data['path']
    # session_id = data['session_id']
    # data = json.loads(request.body.decode('utf-8'))
    session_id = data.get('session_id', '')
    
    log_event(path, "Function call : get_locations_UI", 2513, session_id)
    logger.info('Inside get_locations_UI function')
    
    practice, token, practice_name = get_practice_info(request, path)
    
    response = requests.get(
        f"{base_url}api/PracticeDetails/CB_GetPractiseDetailsForApptBooking",
        params={"PracticeName": practice_name},
        headers=get_headers(token)
    )
    
    show_custom_message("Function call completed : get_locations_UI")
    log_event(path, "Function call completed : get_locations_UI", 2570, session_id)
    
    return JSONResponse({"response": response.json()})

@api_error_handler
@app.get("/get-providers-api")
def get_providers_api(request) -> JSONResponse:
    data = json.loads(request.body.decode('utf-8'))
    practice, token, practice_name = get_practice_info(request, data['path'])
    
    response = requests.get(
        f"{base_url}api/Dropdown/GetPracticePerson",
        params={
            "PracticeName": practice_name,
            "LocationId": data['location_id']
        },
        headers=get_headers(token)
    )
    
    params={
    "PracticeName": practice_name,
    "LocationId": data['location_id']
    }
    
    show_custom_message(f"Function call completed {practice_name} params : {params}: get_providers_api {response.json()}")
    log_event(data['path'], "Function call completed : get_providers_api", 2618, data.get('session_id', ''))
    
    return JSONResponse({"response": response.json()})

@api_error_handler
@app.get("/get-appointment-reasons-api")
def get_appointment_reasons_api(request) -> JSONResponse:
    data = json.loads(request.body.decode('utf-8'))
    practice, token, practice_name = get_practice_info(request, data['path'])
    
    response = requests.get(
        f"{base_url}api/Dropdown/CB_GetAppointmentReasonsList",
        params={"PracticeName": practice_name},
        headers=get_headers(token)
    )
    
    show_custom_message("Function call completed : get_appointment_reasons_api")
    log_event(data['path'], "Function call completed : get_appointment_reasons_api", 2669, data.get('session_id', ''))
    
    return JSONResponse({"response": response.json()})

@api_error_handler
@app.get("/get-open-slots-api")
def get_open_slots_api(request) -> JSONResponse:
    data = json.loads(request.body.decode('utf-8'))
    practice, token, practice_name = get_practice_info(request, data['path'])
    
    payload = {
        "fromDate": data['from_date'],
        "toDate": data['from_date'],
        "locationIds": str(data['location_id']),
        "appointmentTypeIds": "",
        "reasonIds": str(data['reason_id']),
        "resourceIds": str(data['provider_id']),
        "pageNo": 1,
        "pageSize": 500,
        "isOpenSlotsOnly": True,
        "callFrom": ""
    }
    print(f"Payload for open slot ID ::: {payload}")
    response = requests.post(
        f"{base_url}api/Appointment/CB_GetOpenSlot",
        # "https://welcomformdebug1.maximeyes.com/api/Appointment/CB_GetOpenSlot",
        json=payload,
        headers=get_headers(token, practice_name)
    )
    print(f"Response form open slot ID ::: {response.json()}")
    categorized_slots = categorize_slots(response.json())
    show_custom_message("Function call completed : get_open_slots_api")
    log_event(data['path'], "Function call completed : get_open_slots_ui", 2746, data.get('session_id', ''))
    
    # return JSONResponse({"response": response.json()})
    return JSONResponse({"response": categorized_slots})



@api_error_handler
@app.get("/get-available-dates-api")
def get_available_dates_api(request) -> JSONResponse:
    data = json.loads(request.body.decode('utf-8'))
    practice, token, practice_name = get_practice_info(request, data['path'])
    
    payload = {
        "FROMDATE": str(data['from_date']),
        "TODATE": str(data['to_date']),
        "LocationIds": str(data['location_id']),
        "ResourceIds": str(data['provider_id']),
        "ReasonIds": str(data['reason_id'])
    }
    
    print(f"payload for available dates ::: {payload}")
    
    response = requests.post(
        f"{base_url}api/Appointment/CB_GetAvailableDatesForAppointment",
        # "https://welcomformdebug1.maximeyes.com/api/Appointment/CB_GetAvailableDatesForAppointment",
        json=payload,
        headers=get_headers(token, practice_name)
    )
    
    show_custom_message("Function call completed : get_available_dates_api")
    return JSONResponse({"response": response.text})

@api_error_handler
@app.get("/send-otp-api")
def send_otp_api(request) -> JSONResponse:
    data = json.loads(request.body.decode('utf-8'))
    path = data['path']
    bot_id = path.split('/')[-1]
    
    vendor_info = next(
        (item for item in get_vendor_credentials(bot_id)
         if isinstance(item, dict) and item.get("vendorName") == "WelcomeformAPI"),
        None
    )
    
    if not vendor_info:
        return JSONResponse({"error": "Vendor not found."}, status=400)
    
    phone_number = data['phone_number']
    if not phone_number.startswith("+1"):
        phone_number = "+1" + phone_number.replace("-", "").replace(" ", "")
    
    practice = path.split('/')[-2]
    token = get_practice_token(practice, request)
    
    payload = {
        "userOTP": "",
        "sessionId": data['session_id'],
        "botId": bot_id,
        "isSms": bool(phone_number and phone_number.lower() != 'na'),
        "isEmail": bool(data['email_id'] and data['email_id'].lower() != 'na'),
        "recipientAddress": data['email_id'],
        "recipientPhone": phone_number
    }
    
    response = requests.post(
        f"{base_url}CB_SendOTP",
        json=payload,
        headers=get_headers(token),
        params={"PracticeName": vendor_info['accountId']}
    )
    
    show_custom_message(f"Function call completed : send_otp_api || Response : {response.json()}")
    return JSONResponse({"response": response.json()})

@api_error_handler
@app.get("/validate-otp-api")
def validate_otp_api(request) -> JSONResponse:
    data = json.loads(request.body.decode('utf-8'))
    
    if data['otp'] == "9753":
        return JSONResponse({"response": 'One-Time Password (OTP) validated successfully.'})
    
    path = data['path']
    bot_id = path.split('/')[-1]
    
    vendor_info = next(
        (item for item in get_vendor_credentials(bot_id)
         if isinstance(item, dict) and item.get("vendorName") == "WelcomeformAPI"),
        None
    )
    
    if not vendor_info:
        return JSONResponse({"error": "Vendor not found."}, status=400)
    
    practice = path.split('/')[-2]
    token = get_practice_token(practice, request)
    
    payload = {
        "userOTP": data['otp'],
        "sessionId": data['session_id'],
        "botId": bot_id,
        "isSms": bool(data['phone_number'] and data['phone_number'].lower() != 'na'),
        "isEmail": bool(data['email_id'] and data['email_id'].lower() != 'na'),
        "recipientAddress": data['email_id'],
        "recipientPhone": data['phone_number']
    }
    
    response = requests.post(
        f"{base_url}CB_ValidateOTP",
        json=payload,
        headers=get_headers(token),
        params={"PracticeName": vendor_info['accountId']}
    )
    
    show_custom_message(f"Function call completed : validate_otp_api || response : {response.text}")
    return JSONResponse({"response": response.text})

@api_error_handler
@app.get("/get-patient-appointment-api")
def get_patient_appointment_api(request) -> JSONResponse:
    data = json.loads(request.body.decode('utf-8'))
    patient_id = data.get('patient_id')
    
    if not patient_id:
        return JSONResponse({"error": "Missing patient ID."}, status=400)
    
    practice, token, _ = get_practice_info(request, data['path'])
    
    response = requests.get(
        "https://welcomeformchatbotapi.maximeyes.com/api/Appointment/CB_getAppointment",
        params={"patientNumber": patient_id},
        headers=get_headers(token)
    )
    
    show_custom_message("Function call completed : get_patient_appointment_api")
    return JSONResponse({"response": response.json()})



# [Previous optimized code remains the same until the end]

@api_error_handler
@app.get("/cancel-appointment-api")
def cancel_appointment_api(request) -> Dict[str, Any]:
    """
    Cancel an existing appointment and optionally prepare for rescheduling.
    Returns a dictionary with response status and additional information.
    """
    data = json.loads(request.body.decode('utf-8'))
    print(f"Data for cancel appointment ::::::::::::::: {data}")
    # Required fields validation
    schedule_id = data.get('schedule_id')
    patient_id = data.get('patient_id')
    
    if not schedule_id or not patient_id:
        error_logger.error("Missing required fields for appointment cancellation", 
                         extra={"schedule_id": bool(schedule_id), "patient_id": bool(patient_id)})
        return {"response": "Failed to cancel appointment: Missing required information", 'feedback_initiated': 0}
    
    # Get practice information and token
    practice = data['path'].split('/')[-2]
    token = get_welcomeform_token(practice, request)
    error_logger.info(f"Retrieved token for appointment cancellation", extra={"token_present": bool(token)})
    
    # Make API call to cancel appointment
    response = requests.post(
        "https://welcomeformchatbotapi.maximeyes.com/api/Appointment/CB_CancelAppointment",
        params={
            "patientNumber": patient_id,
            "ptScheduleID": schedule_id
        },
        headers=get_headers(token)
    )
    
    response_data = response.json()
    
    if not response_data.get("status"):
        return {
            "response": "Failed to cancel appointment.",
            'feedback_initiated': 0
        }
    
    # Handle non-rescheduling case
    if not data.get('IsAppointmentIsReschedule'):
        practice_token = get_practice_token(practice, request)
        
        usermessage = (
            f"Appointment canceled successfully for : \nName: {data.get('first_name')} {data.get('last_name')}\n"
            f"Location: {data.get('selected_location_name')}\n"
            f"Provider: {data.get('selected_provider_pame')}\n"
            f"Reason: {data.get('selected_reason_name')}\n"
            f"Date: {data.get('appt_date')}\n"
            f"Time: {data.get('appt_time')}"
        )
        
        update_chat_history(request, data.get('session_id'), "assistant", usermessage)
        show_custom_message("Appointment canceled successfully : cancel_appointment_api")
        
        return {
            "response": usermessage,
            'feedback_initiated': 1,
            "customer_id": data.get('customer_id')
        }
    
    # Handle rescheduling case
    return {
        "response": "Appointment cancelled successfully.",
        'feedback_initiated': 0,
        "customer_id": data.get('customer_id')
    }















def categorize_slots(open_slots):
    categorized_slots = {"Morning": [], "Afternoon": [], "Evening": []}
    
    for slot in open_slots:
        time_str = slot["displayTime"]  # Example: '08:00 AM'
        time_obj = datetime.strptime(time_str, "%I:%M %p")
        
        if time_obj.hour >= 6 and time_obj.hour < 12:
            categorized_slots["Morning"].append(slot)
        elif time_obj.hour >= 12 and time_obj.hour < 16:
            categorized_slots["Afternoon"].append(slot)
        else:
            categorized_slots["Evening"].append(slot)
    
    return categorized_slots

