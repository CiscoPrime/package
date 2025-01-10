import paramiko
import json
from collections import defaultdict
import logging


#logging.basicConfig(level=logging.DEBUG)

#paramiko.common.logging.basicConfig(level=logging.DEBUG)
# List of IPs to log into
ip_addresses = ["10.23.255.101"]

# SSH credentials
username = "solarwinds"
password = "TurboQuick5and!"

# Command to execute
commands = ["terminal length 0", "show ip route vrf *"]

def parse_route_output(output):
    """
    Parses the routing table output into a structured dictionary format.
    """
    parsed_data = defaultdict(list)
    current_table = None

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Routing Table:"):
            current_table = line.split(":")[1].strip()
        elif current_table and line and not line.startswith("Codes:") and not line.startswith("Gateway"):
            parsed_data[current_table].append(line)

    return dict(parsed_data)

def ssh_to_device(ip):
    """
    SSH into a device and run commands.
    """
    try:
        # Initialize SSH client
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(ip, username=username, password=password, allow_agent=False, look_for_keys=False)

        # Open an SSH shell
        ssh_shell = client.invoke_shell()
        ssh_shell.send("terminal length 0\n")
        ssh_shell.recv(1024)  # Clearing initial output
       
        # Execute the command
        ssh_shell.send("show ip route vrf *\n")
        output = ""
        while True:
            if ssh_shell.recv_ready():
                output += ssh_shell.recv(1024).decode('utf-8')
            else:
                break

        # Parse and save the output
        parsed_data = parse_route_output(output)
        with open(f"{ip}.json", "w") as json_file:
            json.dump({"raw_output": output}, json_file, indent=4)
            #json.dump(parsed_data, json_file, indent=4)

        print(f"Saved routing table for {ip} to {ip}.json")

        client.close()

    except Exception as e:
        print(f"Failed to connect to {ip}: {str(e)}")

if __name__ == "__main__":
    for ip in ip_addresses:
        ssh_to_device(ip)
