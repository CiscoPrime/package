from ncclient import manager
import os

# Ensure environment compatibility on Windows
# Patching to bypass AF_UNIX on Windows
os.environ["NC_NO_UNIX_SOCKET"] = "1"

# Device connection details
device = {
    "host": "10.23.20.140",
    "port": 830,
    "username": "solarwinds",
    "password": "TurboQuick5and!",
    "hostkey_verify": False
}

# NETCONF filter for the desired command
netconf_filter = """
<rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0" message-id="101">
    <get>
        <filter>
            <show xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-show-ap-profile-oper">
                <ap-profile>
                    <all-profiles/>
                </ap-profile>
            </show>
        </filter>
    </get>
</rpc>
"""

try:
    # Connect to the device using ncclient
    with manager.connect(**device) as m:
        # Execute the NETCONF filter and retrieve the response
        response = m.dispatch(netconf_filter)
        print("Command Output:\n", response.xml)
except Exception as e:
    print(f"An error occurred: {e}")
