import json
from ise_api_client import ISEApiClient
from resources import SUPPORTED_RESOURCES
import argparse
class ISEApi:
    def __init__(self, base_url, username, password):
        self.client = ISEApiClient(base_url, username, password)
        self.session_id = None

    def authenticate(self):
        if not self.session_id:
            print("Authenticating...")
            self.session_id = self.client.login()
            print(f"Session ID: {self.session_id}")

    def execute_request(self, resource_name, **kwargs):
        # Ensure user is authenticated
        self.authenticate()

        # Check if resource is supported
        resource = SUPPORTED_RESOURCES.get(resource_name)
        if not resource:
            raise ValueError(f"Resource '{resource_name}' not supported.")

        # Validate required parameters
        missing_params = [p for p in resource["params"] if p not in kwargs]
        if missing_params:
            raise ValueError(f"Missing required parameters: {', '.join(missing_params)}")

        # Prepare the request
        endpoint = resource["path"]
        method = resource["method"]
        requires_csrf = resource["requires_csrf"]

        print(f"Executing {method} request to endpoint '{endpoint}' with parameters {kwargs}")

        data = {"selectedItemName": kwargs["hostname"]} if resource_name == "sync_action" else kwargs

        response = self.client.send_request(endpoint, method=method, data=data, requires_csrf=requires_csrf, resource_name=resource_name)
        if response:
            print("Response:")
            print(response)
        else:
            print("No data returned.")

    def cleanup(self):
        """Clean up session by logging out."""
        self.client.logout()

def main():
    base_url = "https://10.23.18.218"  # Corrected to string
    username = "ERS"
    password = "RapidQuick5and!"

    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Cisco ISE API CLI")
    parser.add_argument("--resource", required=True, help="Name of the API resource to query")
    parser.add_argument("--params", nargs="*", help="Key=value pairs for resource parameters", default=[])

    args = parser.parse_args()

    # Convert params to dictionary
    params_dict = {}
    for param in args.params:
        key, value = param.split("=")
        params_dict[key] = value

    api = ISEApi(base_url, username, password)

    try:
        api.execute_request(args.resource, **params_dict)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always log out to prevent session buildup
        api.cleanup()

if __name__ == "__main__":
    main()