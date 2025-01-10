import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Disable insecure request warnings
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# URLs and credentials
login_url = "https://10.23.18.218/admin/LoginAction.do"
admin_page_url = "https://10.23.18.218/admin/"
syncup_url = "https://10.23.18.218/admin/syncupAction.do"

payload = {
    "username": "ERS",
    "password": "RapidQuick5and!",
    "authType": "Internal",
    "rememberme": "on",
    "name": "ERS",
    "locale": "en",
    "hasSelectedLocale": "false"
}

def create_new_session():
    session = requests.Session()
    print("Performing login request...")
    response = session.post(login_url, data=payload, verify=False, allow_redirects=True)

    if response.status_code in [200, 302]:
        session_id = session.cookies.get("APPSESSIONID")
        if not session_id:
            raise ValueError("APPSESSIONID not found in cookies.")
        print(f"New session created with APPSESSIONID: {session_id}")
        return session
    else:
        raise ValueError(f"Login failed with status code: {response.status_code}, response: {response.text}")

def get_csrf_token(session):
    print("Fetching CSRF token from admin page...")
    cookies = {"APPSESSIONID": session.cookies.get("APPSESSIONID")}
    response = session.get(admin_page_url, cookies=cookies, verify=False)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch admin page. Status code: {response.status_code}")

    # Parse the HTML to get the CSRF token
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'CSRFTokenNameValue'})
    if csrf_input:
        csrf_token = csrf_input['value'].split("OWASP_CSRFTOKEN=")[-1]
        print(f"Extracted CSRF token: {csrf_token}")
        return csrf_token
    else:
        raise ValueError("CSRF token not found on the admin page.")

def syncup_action(session, csrf_token):
    cookies = {
        "networkDevicequickFilterNotification": "true",
        "APPSESSIONID": session.cookies.get("APPSESSIONID"),
        "SaveStateCookie": "root"
    }

    headers = {
        "Connection": "keep-alive",
        "Cache-Control": "max-age=0",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "sec-ch-ua": "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"90\", \"Google Chrome\";v=\"90\"",
        "sec-ch-ua-mobile": "?0",
        "Referer": "https://10.23.18.218/admin/login.jsp",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "_QPH_": "Y29tbWFuZD1zeW5jdXBEQg==",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://10.23.18.218",
        "OWASP_CSRFTOKEN": csrf_token,
        "X-Requested-With": "XMLHttpRequest"
    }

    data = {
        "selectedItemName": "HO-FRN-ISE-04S"
    }

    print("Performing sync-up request...")
    response = session.post(syncup_url, headers=headers, cookies=cookies, data=data, verify=False)

    print(f"Response Status Code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    if response.status_code == 200:
        print("Sync-up action successful.")
        print("Full Response Text:", response.text)
    else:
        print(f"Failed to perform sync-up. Status code: {response.status_code}")
        print(f"Response Text: {response.text}")

try:
    session = create_new_session()
    csrf_token = get_csrf_token(session)
    syncup_action(session, csrf_token)

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
except ValueError as ve:
    print(f"Error: {ve}")
