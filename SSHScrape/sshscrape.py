import paramiko
import json
import xml.dom.minidom as minidom
from concurrent.futures import ThreadPoolExecutor
import time
import os
import xmltodict  # Library to convert XML to JSON

def load_device_config(config_file):
    """
    Load the device configuration from a JSON file.
    """
    with open(config_file, 'r') as file:
        return json.load(file)

def clean_xml_output(raw_output):
    """
    Clean the raw output to extract only XML.

    Args:
        raw_output (str): Raw command output.

    Returns:
        str: Cleaned XML string.
    """
    try:
        start_idx = raw_output.find('<?xml')
        end_idx = raw_output.rfind('</ShowIpRoute>') + len('</ShowIpRoute>')
        if start_idx != -1 and end_idx != -1:
            return raw_output[start_idx:end_idx].strip()
        else:
            return ""  # Return empty if XML markers are not found.
    except Exception as e:
        return f"<!-- Error parsing XML: {str(e)} -->"

def ssh_command_execution(host, username, password, base_commands, command_settings):
    """
    SSH into a device and execute commands.

    Args:
        host (str): IP address of the device.
        username (str): SSH username.
        password (str): SSH password.
        base_commands (list): List of base commands to execute.
        command_settings (dict): Dictionary with command-specific settings.

    """
    vrf_list = []

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=username, password=password, timeout=10)

        shell = ssh.invoke_shell()
        shell.settimeout(10)

        # Set terminal length to 0 to prevent pagination
        shell.send("terminal length 0\n")
        time.sleep(1)
        buffer = ""
        while shell.recv_ready():
            buffer += shell.recv(4096).decode('utf-8')

        # Step 1: Execute "show run vrf | in ^ip vrf" if needed and extract VRFs
        for base_command in base_commands:
            if base_command == "show run vrf | in ^ip vrf":
                shell.send("show run vrf | in ^ip vrf\n")
                time.sleep(1)
                buffer = ""
                while True:
                    if shell.recv_ready():
                        response = shell.recv(4096).decode('utf-8')
                        buffer += response
                        if buffer.endswith('#') or "--More--" in buffer:
                            break

                while "--More--" in buffer:
                    shell.send(" ")  # Send a space to continue output
                    time.sleep(1)
                    buffer += shell.recv(4096).decode('utf-8')

                for line in buffer.strip().splitlines():
                    if line.startswith("ip vrf"):
                        vrf_name = line.split()[-1]
                        vrf_list.append(vrf_name)

        # Step 2: Execute other commands, replacing "XVARIABLE" with VRFs if applicable
        for base_command in base_commands:
            if base_command != "show run vrf | in ^ip vrf":
                if "XVARIABLE" in base_command and vrf_list:
                    for vrf_name in vrf_list:
                        command = base_command.replace("XVARIABLE", vrf_name)
                        shell.send(command + "\n")
                        buffer = ""
                        while True:
                            if shell.recv_ready():
                                response = shell.recv(4096).decode('utf-8')
                                buffer += response
                                if buffer.endswith('#') or "--More--" in buffer:
                                    break

                        while "--More--" in buffer:
                            shell.send(" ")
                            time.sleep(1)
                            buffer += shell.recv(4096).decode('utf-8')

                        command_output = buffer.strip()
                        cleaned_output = clean_xml_output(command_output)

                        # Convert XML to JSON
                        if cleaned_output:
                            try:
                                json_output = json.dumps(xmltodict.parse(cleaned_output), indent=4)
                            except Exception as e:
                                json_output = json.dumps({"error": f"Failed to convert XML to JSON: {str(e)}"}, indent=4)

                            # Save JSON to a file
                            output_file_path = f"device_outputs/{host.replace('.', '_')}_{vrf_name}.json"
                            with open(output_file_path, 'w') as json_file:
                                json_file.write(json_output)
                else:
                    shell.send(base_command + "\n")
                    buffer = ""
                    while True:
                        if shell.recv_ready():
                            response = shell.recv(4096).decode('utf-8')
                            buffer += response
                            if buffer.endswith('#') or "--More--" in buffer:
                                break

                    while "--More--" in buffer:
                        shell.send(" ")
                        time.sleep(1)
                        buffer += shell.recv(4096).decode('utf-8')

                    command_output = buffer.strip()
                    cleaned_output = clean_xml_output(command_output)

                    # Convert XML to JSON
                    if cleaned_output:
                        try:
                            json_output = json.dumps(xmltodict.parse(cleaned_output), indent=4)
                        except Exception as e:
                            json_output = json.dumps({"error": f"Failed to convert XML to JSON: {str(e)}"}, indent=4)

                        # Save JSON to a file
                        output_file_path = f"device_outputs/{host.replace('.', '_')}_{base_command.replace(' ', '_')}.json"
                        with open(output_file_path, 'w') as json_file:
                            json_file.write(json_output)

        ssh.close()
    except Exception as e:
        error_message = f"Error connecting to {host}: {str(e)}"
        error_file_path = f"device_outputs/{host.replace('.', '_')}_error.txt"
        with open(error_file_path, 'w') as error_file:
            error_file.write(error_message)

def scrape_devices(config_file, output_dir):
    """
    Main function to scrape devices and store the output.

    Args:
        config_file (str): Path to the JSON config file.
        output_dir (str): Directory to store JSON output files.
    """
    config = load_device_config(config_file)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    def process_device(device):
        host = device['ip']
        device_type = device['type']
        username = device['username']
        password = device['password']
        base_commands = config['device_commands'].get(device_type, [])
        command_settings = config.get('command_settings', {})

        ssh_command_execution(host, username, password, base_commands, command_settings)

    # Using ThreadPoolExecutor for parallel execution
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_device, config['devices'])

if __name__ == '__main__':
    CONFIG_FILE = 'device_config.json'
    OUTPUT_DIR = 'device_outputs'

    scrape_devices(CONFIG_FILE, OUTPUT_DIR)
