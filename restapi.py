# Flask REST API to restart an Access Point via NETCONF using ncclient
from flask import Flask, request, jsonify
from ncclient import manager

# Monkey patch to disable UnixSocketSession for Windows (force AF_UNIX to None)
import sys
if sys.platform == "win32":
    from ncclient.transport import unixSocket
    unixSocket.UnixSocketSession = None  # Prevent usage of Unix sockets on Windows

# Create Flask app
app = Flask(__name__)

# Endpoint to restart Access Point
@app.route('/restart_ap', methods=['POST'])
def restart_ap():
    # Get AP name from the request body
    ap_name = request.json.get("ap_name")
    if not ap_name:
        return jsonify({"error": "AP name is required"}), 400

    try:
        # NETCONF connection to WLC
        with manager.connect(
            host='WLC_IP',  # Replace with your Cisco 9800 WLC IP
            port=830,  # NETCONF port (default for SSH)
            username='your_username',  # Replace with your WLC username
            password='your_password',  # Replace with your WLC password
            hostkey_verify=False  # Disable host key verification (use cautiously)
        ) as m:
            # NETCONF RPC XML to restart the access point
            rpc_command = f"""
            <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
                <action xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-rpc">
                    <restart-ap>
                        <ap-name>{ap_name}</ap-name>
                    </restart-ap>
                </action>
            </rpc>
            """
            # Send the RPC command
            response = m.dispatch(rpc_command)
            return jsonify({"status": "success", "response": str(response)}), 200

    except Exception as e:
        return jsonify({"status": "failure", "error": str(e)}), 500


# Start the Flask app
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
