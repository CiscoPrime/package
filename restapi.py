from ncclient import manager
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/restart_ap', methods=['POST'])
def restart_ap():
    ap_name = request.json.get("ap_name")
    with manager.connect(
        host='WLC_IP',
        port=830,
        username='your_username',
        password='your_password',
        hostkey_verify=False
    ) as m:
        rpc_command = f"""
        <rpc xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <action xmlns="http://cisco.com/ns/yang/Cisco-IOS-XE-rpc">
                <restart-ap>
                    <ap-name>{ap_name}</ap-name>
                </restart-ap>
            </action>
        </rpc>
        """
        response = m.dispatch(rpc_command)
        return jsonify({"status": "success", "response": str(response)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
