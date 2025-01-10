
import subprocess
import json
import os
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable warnings for unverified HTTPS requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# URLs and credentials
login_url = "https://10.23.18.218/admin/LoginAction.do"
get_url = "https://10.23.18.218/admin/rs/uiapi/mnt/reports/reportStore"
token_file = "token.txt"

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

def run_curl_with_token(session_id):
    curl_command = [
        "curl",
        get_url,
        "-H", "Connection: keep-alive",
        "-H", 'sec-ch-ua: \" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\", \"Google Chrome\";v=\"90\"',
        "-H", "Accept: application/json, text/javascript, */*; q=0.01",
        "-H", "OWASP_CSRFTOKEN: CMNK-K8TM-S3OM-KU2H-02MP-VIZ2-KHM5-J6B9",
        "-H", "X-Requested-With: XMLHttpRequest, XMLHttpRequest",
        "-H", "sec-ch-ua-mobile: ?0",
        "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
        "-H", "Sec-Fetch-Site: same-origin",
        "-H", "Sec-Fetch-Mode: cors",
        "-H", "Sec-Fetch-Dest: empty",
        "-H", "Referer: https://10.23.18.218/admin/",
        "-H", "Accept-Language: en-GB,en-US;q=0.9,en;q=0.8",
        f"-H", f"Cookie: networkDevicequickFilterNotification=true; APPSESSIONID={session_id}",
        "--compressed",
        "--insecure"
    ]

    try:
        result = subprocess.run(
            curl_command,
            capture_output=True,
            text=True,
            check=True
        )
        response_text = result.stdout

        # Debugging: Print raw response
        print("Raw Response:", response_text)

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            print("Failed to decode JSON. Raw response returned instead.")
            data = {"raw_response": response_text}

        # Save the data to a JSON file
        resource_name = "reports.json"
        with open(resource_name, "w") as file:
            json.dump(data, file, indent=4)

        print(f"Data successfully saved to {resource_name}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running the curl command: {e}")
        print(f"Command Output: {e.output}")

def fetch_data():
    try:
        token = read_token()
        if token:
            print("Using token from token.txt")
            try:
                run_curl_with_token(token)
            except ValueError:
                print("Stored token invalid or expired. Creating a new session.")
                token = create_new_session()
                run_curl_with_token(token)
        else:
            print("No token found. Creating a new session.")
            token = create_new_session()
            run_curl_with_token(token)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    fetch_data()
