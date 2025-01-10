from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import requests
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
from resources import SUPPORTED_RESOURCES

class ISEApiClient:
    def __init__(self, base_url, username, password):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.session = requests.Session()

    def login(self):
        login_url = f"{self.base_url}/admin/LoginAction.do"
        payload = {
            "username": self.username,
            "password": self.password,
            "authType": "Internal",
            "rememberme": "on",
            "name": self.username,
            "locale": "en",
            "hasSelectedLocale": "false"
        }
        print(f"Logging in to {login_url}...")
        response = self.session.post(login_url, data=payload, verify=False, allow_redirects=False)

        if response.status_code == 302:
            session_id = self.session.cookies.get("APPSESSIONID")
            if not session_id:
                raise ValueError("Login failed: session ID not found.")
            print(f"Login successful. Session ID: {session_id}")
            return session_id
        else:
            raise ValueError(f"Login failed. Status Code: {response.status_code}, Response: {response.text}")

    def get_csrf_token(self):
        admin_page_url = f"{self.base_url}/admin/"
        print(f"Fetching CSRF token from {admin_page_url}...")
        response = self.session.get(admin_page_url, verify=False)

        if response.status_code != 200:
            raise ValueError(f"Failed to access admin page. Status code: {response.status_code}")

        soup = BeautifulSoup(response.text, "html.parser")
        csrf_input = soup.find("input", {"name": "CSRFTokenNameValue"})
        if csrf_input:
            csrf_token = csrf_input['value'].split("OWASP_CSRFTOKEN=")[-1]
            print(f"Extracted CSRF Token: {csrf_token}")
            return csrf_token
        else:
            raise ValueError("CSRF token not found.")

    def send_request(self, endpoint, method="GET", data=None, requires_csrf=False, resource_name=None):
        # Default headers
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Referer": f"{self.base_url}/admin/login.jsp"
        }
    
        # CSRF token if required
        if requires_csrf:
            csrf_token = self.get_csrf_token()
            headers["OWASP_CSRFTOKEN"] = csrf_token
    
        # Add resource-specific headers from SUPPORTED_RESOURCES
        resource_headers = SUPPORTED_RESOURCES.get(resource_name, {}).get("headers", {})
        headers.update(resource_headers)  # Merge default headers with resource-specific headers
    
        # Cookies
        cookies = {
            "APPSESSIONID": self.session.cookies.get("APPSESSIONID"),
            "networkDevicequickFilterNotification": "true",
            "SaveStateCookie": "root"
        }
    
        url = f"{self.base_url}/{endpoint}"
        print(f"Sending {method} request to {url} with resource: {resource_name}...")
    
        # Send the request
        response = self.session.request(method, url, headers=headers, cookies=cookies, data=data, verify=False)
    
        print(f"Response Status Code: {response.status_code}")
        if "<html" in response.text.lower():
            print("Error: Received an HTML page (likely a redirect to the login page).")
        if response.status_code not in [200, 201]:
            print(f"Failed request. Response: {response.text}")
            return None
        return response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text

    def logout(self):
        logout_url = f"{self.base_url}/admin/logout.jsp"
        print("Logging out...")
        response = self.session.get(logout_url, verify=False)

        if response.status_code in [200, 302]:
            print("Successfully logged out.")
        else:
            print(f"Logout failed. Status Code: {response.status_code}")
