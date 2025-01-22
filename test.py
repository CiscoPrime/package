from ncclient import manager

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

# Connect to the device and execute the command
try:
    with manager.connect(**device) as m:
        response = m.dispatch(netconf_filter)
        print(response.xml)  # Print the response from the WLC
except Exception as e:
    print(f"Error: {e}")
