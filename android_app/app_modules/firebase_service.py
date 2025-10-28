import requests
import json
from config import API_KEY, PROJECT_ID
import datetime

SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={API_KEY}"
LOGIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

def sign_up(email, password):
    """Creates a new user with the given email and password using Firebase Auth REST API."""
    payload = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    try:
        r = requests.post(SIGNUP_URL, data=payload)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as err:
        print(f"Error creating user: {err.response.text}")
        return err.response.json()

def login(email, password):
    """Signs in a user with the given email and password using Firebase Auth REST API."""
    payload = json.dumps({"email": email, "password": password, "returnSecureToken": True})
    try:
        r = requests.post(LOGIN_URL, data=payload)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as err:
        print(f"Error logging in: {err.response.text}")
        return err.response.json()

def add_reminder(id_token, user_id, title, description, reminder_time):
    """Adds a new reminder to Firestore using the REST API."""
    url = f"{FIRESTORE_URL}/users/{user_id}/reminders"
    headers = {"Authorization": f"Bearer {id_token}"}
    try:
        reminder_dt = datetime.datetime.strptime(reminder_time, "%Y-%m-%d %H:%M")
        timestamp_str = reminder_dt.isoformat() + "Z"
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD HH:MM")
        return False

    payload = {"fields": {
        "title": {"stringValue": title},
        "description": {"stringValue": description},
        "reminder_time": {"timestampValue": timestamp_str},
        "is_active": {"booleanValue": True}
    }}
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        print(f"Error adding reminder: {err.response.text}")
        return False

def get_reminders(id_token, user_id):
    """Retrieves all reminders for a user, including their IDs."""
    url = f"{FIRESTORE_URL}/users/{user_id}/reminders"
    headers = {"Authorization": f"Bearer {id_token}"}
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        response_data = r.json().get('documents', [])
        reminders = []
        for doc in response_data:
            doc_id = doc.get('name', '').split('/')[-1]
            fields = doc.get('fields', {})
            reminders.append({
                'id': doc_id,
                'title': fields.get('title', {}).get('stringValue', ''),
                'reminder_time': fields.get('reminder_time', {}).get('timestampValue', '')
            })
        return reminders
    except requests.exceptions.HTTPError as err:
        print(f"Error getting reminders: {err.response.text}")
        return []

def delete_reminder(id_token, user_id, reminder_id):
    """Deletes a specific reminder from Firestore."""
    url = f"{FIRESTORE_URL}/users/{user_id}/reminders/{reminder_id}"
    headers = {"Authorization": f"Bearer {id_token}"}
    try:
        r = requests.delete(url, headers=headers)
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        print(f"Error deleting reminder: {err.response.text}")
        return False

def update_reminder(id_token, user_id, reminder_id, reminder_data):
    """Updates a specific reminder in Firestore."""
    url = f"{FIRESTORE_URL}/users/{user_id}/reminders/{reminder_id}"
    headers = {"Authorization": f"Bearer {id_token}"}

    try:
        reminder_dt = datetime.datetime.strptime(reminder_data['reminder_time'], "%Y-%m-%d %H:%M")
        timestamp_str = reminder_dt.isoformat() + "Z"
    except (ValueError, KeyError):
        print("Invalid or missing date format. Please use YYYY-MM-DD HH:MM")
        return False

    payload = {"fields": {
        "title": {"stringValue": reminder_data.get('title', '')},
        "description": {"stringValue": reminder_data.get('description', '')},
        "reminder_time": {"timestampValue": timestamp_str}
    }}

    try:
        r = requests.patch(url, headers=headers, json=payload)
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        print(f"Error updating reminder: {err.response.text}")
        return False

def add_booking(id_token, user_id, booking_type, confirmation, departure, arrival):
    """Adds a new booking to Firestore using the REST API."""
    url = f"{FIRESTORE_URL}/users/{user_id}/bookings"
    headers = {"Authorization": f"Bearer {id_token}"}
    try:
        departure_dt = datetime.datetime.strptime(departure, "%Y-%m-%d %H:%M")
        arrival_dt = datetime.datetime.strptime(arrival, "%Y-%m-%d %H:%M")
        departure_ts = departure_dt.isoformat() + "Z"
        arrival_ts = arrival_dt.isoformat() + "Z"
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD HH:MM")
        return False

    payload = {"fields": {
        "booking_type": {"stringValue": booking_type},
        "confirmation_number": {"stringValue": confirmation},
        "departure_date": {"timestampValue": departure_ts},
        "arrival_date": {"timestampValue": arrival_ts}
    }}
    try:
        r = requests.post(url, headers=headers, json=payload)
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        print(f"Error adding booking: {err.response.text}")
        return False

def get_bookings(id_token, user_id):
    """Retrieves all bookings for a user, including their IDs."""
    url = f"{FIRESTORE_URL}/users/{user_id}/bookings"
    headers = {"Authorization": f"Bearer {id_token}"}
    try:
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        response_data = r.json().get('documents', [])
        bookings = []
        for doc in response_data:
            doc_id = doc.get('name', '').split('/')[-1]
            fields = doc.get('fields', {})
            bookings.append({
                'id': doc_id,
                'booking_type': fields.get('booking_type', {}).get('stringValue', ''),
                'confirmation_number': fields.get('confirmation_number', {}).get('stringValue', '')
            })
        return bookings
    except requests.exceptions.HTTPError as err:
        print(f"Error getting bookings: {err.response.text}")
        return []

def delete_booking(id_token, user_id, booking_id):
    """Deletes a specific booking from Firestore."""
    url = f"{FIRESTORE_URL}/users/{user_id}/bookings/{booking_id}"
    headers = {"Authorization": f"Bearer {id_token}"}
    try:
        r = requests.delete(url, headers=headers)
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        print(f"Error deleting booking: {err.response.text}")
        return False

def update_booking(id_token, user_id, booking_id, booking_data):
    """Updates a specific booking in Firestore."""
    url = f"{FIRESTORE_URL}/users/{user_id}/bookings/{booking_id}"
    headers = {"Authorization": f"Bearer {id_token}"}

    try:
        departure_dt = datetime.datetime.strptime(booking_data['departure_date'], "%Y-%m-%d %H:%M")
        arrival_dt = datetime.datetime.strptime(booking_data['arrival_date'], "%Y-%m-%d %H:%M")
        departure_ts = departure_dt.isoformat() + "Z"
        arrival_ts = arrival_dt.isoformat() + "Z"
    except (ValueError, KeyError):
        print("Invalid or missing date format. Please use YYYY-MM-DD HH:MM")
        return False

    payload = {"fields": {
        "booking_type": {"stringValue": booking_data.get('booking_type', '')},
        "confirmation_number": {"stringValue": booking_data.get('confirmation_number', '')},
        "departure_date": {"timestampValue": departure_ts},
        "arrival_date": {"timestampValue": arrival_ts}
    }}

    try:
        r = requests.patch(url, headers=headers, json=payload)
        r.raise_for_status()
        return True
    except requests.exceptions.HTTPError as err:
        print(f"Error updating booking: {err.response.text}")
        return False
