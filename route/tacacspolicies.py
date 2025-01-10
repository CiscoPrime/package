import requests
import json
import os

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# URLs and credentials
login_url = "https://10.23.18.218/admin/LoginAction.do"
get_url = "https://10.23.18.218/admin/rs/uiapi/policytable/tacacs"

payload = {
    "username": "ERS",
    "password": "RapidQuick5and!",
    "authType": "Internal",
    "rememberme": "on",
    "name": "ERS",
    "locale": "en",
    "hasSelectedLocale": "false"
}

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "Referer": "https://10.23.18.218/admin/login.jsp",
    "Origin": "https://10.23.18.218"
}

token_file = "token.txt"

def read_token():
    if os.path.exists(token_file):
        with open(token_file, "r") as file:
            return file.read().strip()
    return None

def write_token(token):
    with open(token_file, "w") as file:
        file.write(token)

def create_new_session():
    session = requests.Session()
    response = session.post(login_url, data=payload, headers=headers, verify=False, allow_redirects=False)

    if response.status_code == 302:  # Successful login with redirect
        session_id = session.cookies.get("APPSESSIONID")
        if not session_id:
            raise ValueError("APPSESSIONID not found in cookies. Check the server response.")
        write_token(session_id)
        return session_id
    else:
        raise ValueError(f"Login failed with status code: {response.status_code}, response: {response.text}")

def fetch_data(session_id):
    cookies = {
        "networkDevicequickFilterNotification": "true",
        "APPSESSIONID": session_id
    }

    response = requests.get(get_url, cookies=cookies, verify=False)
    if response.status_code == 200:
        data = response.json()
        resource_name = "tacacs.json"
        with open(resource_name, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {resource_name}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print(f"Response: {response.text}")

try:
    token = read_token()
    if token:
        print("Using token from token.txt")
        try:
            fetch_data(token)
        except ValueError:
            print("Stored token invalid or expired. Creating a new session.")
            token = create_new_session()
            fetch_data(token)
    else:
        print("No token found. Creating a new session.")
        token = create_new_session()
        fetch_data(token)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
