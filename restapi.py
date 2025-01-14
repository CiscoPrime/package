from ncclient import manager
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/restart_ap', methods=['POST'])
def restart_ap():
    ap_name = request.json.get("HO-HDC-AP012-02")
    with manager.connect(
        host='10.23.20.140',
        port=830,
        username='p-langles3',
        password='Bo?VrPu9yz+IE*n4dEJh',
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
