import requests

# Disable SSL warnings (for self-signed certificates)
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Login URL and credentials
url = "https://10.23.18.218/admin/LoginAction.do"
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

try:
    # Perform login request
    session = requests.Session()  # Use a session to manage cookies
    response = session.post(url, data=payload, headers=headers, verify=False, allow_redirects=False)

    # Check for 302 redirect
    if response.status_code == 302:
        # Extract the APPSESSIONID from cookies
        session_id = session.cookies.get("APPSESSIONID")
        if session_id:
            print(f"Session ID: {session_id}")
        else:
            print("APPSESSIONID not found in cookies. Check the server response.")
    else:
        print(f"Unexpected status code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Body: {response.text}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
