import paramiko
import time
import json
import threading
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("cisco_mapper.log"),
        logging.StreamHandler()
    ]
)

class CiscoCommandMapper:
    def __init__(self, hostname, username, password, port=22, timeout=10):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.port = port
        self.timeout = timeout
        self.ssh_client = None
        self.shell = None
        self.output = ""
        self.lock = threading.Lock()
        self.logger = logging.getLogger(self.__class__.__name__)

    def connect(self):
        """
        Establish an SSH connection and open an interactive shell.
        """
        self.logger.debug(f"Connecting to {self.hostname}:{self.port} as {self.username}")
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       
        try:
            self.ssh_client.connect(
                hostname=self.hostname,
                port=self.port,
                username=self.username,
                password=self.password,
                look_for_keys=False,
                allow_agent=False,
                timeout=self.timeout
            )
            self.logger.debug("SSH connection established successfully.")
           
            # Open an interactive shell session
            self.shell = self.ssh_client.invoke_shell()
            self.logger.debug("Interactive shell session opened.")
           
            # Start a thread to continuously read from the shell
            read_thread = threading.Thread(target=self._read_from_shell, daemon=True)
            read_thread.start()
           
            # Allow some time for the shell to be ready
            time.sleep(1)
           
            # Clear any initial output (like welcome messages)
            with self.lock:
                self.output = ""
           
            # Disable pagination
            self.disable_pagination()
           
        except paramiko.AuthenticationException:
            self.logger.error("Authentication failed, please verify your credentials.")
            raise
        except paramiko.SSHException as sshException:
            self.logger.error(f"Unable to establish SSH connection: {sshException}")
            raise
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            raise

    def _read_from_shell(self):
        """
        Continuously read output from the shell.
        """
        while True:
            if self.shell.recv_ready():
                data = self.shell.recv(1024).decode('utf-8', errors='ignore')
                with self.lock:
                    self.output += data
                self.logger.debug(f"Received data:\n{data}")
            else:
                time.sleep(0.1)

    def send_partial_command(self, command_fragment, delay=0.1, trigger_tab=True):
        """
        Sends a partial command character by character with an optional Tab trigger.
       
        :param command_fragment: The partial command to send (e.g., 'show ').
        :param delay: Delay between sending each character (in seconds).
        :param trigger_tab: Whether to send a Tab character after the command.
        """
        self.logger.debug(f"Sending partial command: '{command_fragment}'")
        for char in command_fragment:
            self.shell.send(char)
            time.sleep(delay)  # Adjust delay as needed for the device to process
        if trigger_tab:
            self.shell.send('\t')  # Send Tab to trigger suggestions
            self.logger.debug("Sent Tab character to trigger suggestions.")

    def send_command_and_get_suggestions(self, command_fragment, wait_time=3):
        """
        Send a partial command and wait for suggestions.
       
        :param command_fragment: The partial command to send (e.g., 'show ').
        :param wait_time: Time to wait for the device to respond with suggestions (in seconds).
        :return: A list of suggested commands.
        """
        self.send_partial_command(command_fragment)
        self.logger.debug(f"Waiting for {wait_time} seconds to receive suggestions.")
        time.sleep(wait_time)  # Wait for device to process and respond
       
        with self.lock:
            output = self.output
            self.output = ""  # Clear after reading
       
        suggestions = self.parse_suggestions(output)
        return suggestions

    def parse_suggestions(self, output):
        """
        Parse the output to extract command suggestions.
       
        :param output: The raw output from the device.
        :return: A list of suggested commands.
        """
        suggestions = []
        lines = output.splitlines()
        for line in lines:
            # Example parsing logic; adjust based on actual output format
            if 'show ' in line and line.strip().startswith('show '):
                # Remove the echoed 'show ' if present
                cmd = line.strip().replace('show ', '', 1)
                suggestions.append(f"show {cmd}")
        self.logger.debug(f"Parsed suggestions: {suggestions}")
        return suggestions

    def disable_pagination(self):
        """
        Disable pagination to receive all output at once.
        """
        self.send_partial_command("terminal length 0", trigger_tab=False)
        time.sleep(1)
        with self.lock:
            self.output = ""  # Clear the buffer
        self.logger.debug("Pagination disabled.")

    def save_output(self, data, filename="command_output.json"):
        """
        Save the captured output to a JSON file.
        """
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
        self.logger.debug(f"Output saved to {filename}")

    def disconnect(self):
        """
        Close the SSH session.
        """
        if self.ssh_client:
            self.ssh_client.close()
            self.logger.debug("Disconnected from SSH.")


# Example usage
if __name__ == "__main__":
    hostname = "10.232.62.130"
    username = os.getenv('SSH_USERNAME', 'admin')  # Default to 'admin' if not set
    password = os.getenv('SSH_PASSWORD', 'Quick5and')  # Default to 'Quick5and' if not set
   
    cisco_mapper = CiscoCommandMapper(hostname, username, password)
   
    try:
        cisco_mapper.connect()
        # Send partial command "show " and trigger suggestions
        partial_command = "show "
        suggestions = cisco_mapper.send_command_and_get_suggestions(partial_command, wait_time=3)
        cisco_mapper.save_output({"command": partial_command, "suggestions": suggestions})
    except Exception as e:
        logging.error(f"ERROR: {e}")
    finally:
        cisco_mapper.disconnect()
