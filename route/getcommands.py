import paramiko
import time
import json
import re
 
class CiscoCommandMapper:
    def __init__(self, hostname, username, password, max_range_size=3):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.ssh_client = None
        self.shell = None
        self.visited_commands = set()
        self.skip_commands = {"enable", "logout"}
        self.range_pattern = re.compile(r"<(\d+)-(\d+)>")
        self.MAX_RANGE_SIZE = max_range_size
 
    def connect(self):
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_client.connect(self.hostname, username=self.username, password=self.password, look_for_keys=False, allow_agent=False)
        self.shell = self.ssh_client.invoke_shell()
        self.shell.resize_pty(width=1500, height=1500)
        time.sleep(2)
        self.shell.recv(65535)
        # Optional: Set terminal length 0
        self.shell.send("terminal length 0\n")
        time.sleep(3)
        self.shell.recv(65535)
 
    def send_command(self, command):
        """
        Send the command followed by a newline and return the output.
        We'll use the 'command + " ?"' pattern and then parse the output
        even if the device complains about incomplete commands.
        """
        print(f"DEBUG: Sending command: '{command}'")
        self.shell.send(command + chr(3))
        time.sleep(0.08)
        output = self.shell.recv(65535).decode('utf-8', errors='replace')
        print("DEBUG: Raw output received:")
        print(output)
        return output
 
    def parse_commands(self, output, base_command=""):
        print(f"this is the raw output....{output}")
        print("Parsing output...")
        lines = output.splitlines()
 
        commands = []
        numeric_ranges = []
 
        # Recognize these error terms
        error_terms = ["Unrecognized command", "Invalid input detected",
                       "Bad IP address", "% Incomplete command.", "Error:"]
 
        prompt_pattern = re.compile(r'^[^>]+>$')
 
        for line in lines:
            line = line.strip('\r')
            if not line.strip():
                continue
 
            # If we hit the device prompt line, stop parsing further
            if prompt_pattern.match(line.strip()):
                break
 
            # If we see an error line, stop parsing at that point, but keep what we parsed before
            if any(err in line for err in error_terms):
                break
 
            # Check for numeric ranges like <0-5>
            range_match = self.range_pattern.search(line)
            if range_match:
                start = int(range_match.group(1))
                end = int(range_match.group(2))
                numeric_ranges.append((start, end))
                continue
 
            # Commands typically start with two spaces in help output
            if not line.startswith("  "):
                continue
 
            parts = line.strip().split(None, 1)
            if not parts:
                continue
            cmd = parts[0]
 
            # Avoid repeating the base command
            if cmd == base_command:
                continue
 
            if cmd not in commands:
                commands.append(cmd)
 
        print(f"Parsed commands: {commands}, Ranges: {numeric_ranges}")
        return commands, numeric_ranges
 
    def map_commands(self, base_command="", depth=0, max_depth=3):
        """
        Map commands recursively up to a certain depth.
        """
        # Stop recursion if depth exceeds the max depth
        if depth > max_depth:
            print(f"Maximum depth of {max_depth} reached. Stopping exploration of '{base_command}'.")
            return {}

        # Check if the base command should be skipped
        for part in base_command.split():
            if part in self.skip_commands:
                print(f"Skipping exploration of '{base_command}' because it's in skip_commands.")
                return {}

        indent = "  " * depth

        # Send command as 'base_command + " ?"' to request help
        if base_command:
            output = self.send_command(base_command + " ?")
        else:
            #output = self.send_command("terminal length 0\n")
            output = self.send_command("?")

        commands, numeric_ranges = self.parse_commands(output, base_command=base_command)

        command_tree = {}

        # Explore regular commands
        for command in commands:
            if command in self.skip_commands:
                print(f"Skipping '{command}' command since it's in skip_commands.")
                command_tree[command] = {}
                continue

            full_command = f"{base_command} {command}".strip()
            if full_command in self.visited_commands:
                continue
            self.visited_commands.add(full_command)

            print(f"{indent}Exploring: {full_command}")
            sub_tree = self.map_commands(full_command, depth + 1, max_depth)
            command_tree[command] = sub_tree if sub_tree else {}

        # Explore numeric ranges
        for (start, end) in numeric_ranges:
            size = end - start + 1
            if size > self.MAX_RANGE_SIZE:
                print(f"{indent}Skipping large range <{start}-{end}> for '{base_command}'")
                samples = [start, (start + end) // 2, end]
                for s in samples:
                    numeric_command = f"{base_command} {s}".strip()
                    if numeric_command in self.visited_commands:
                        continue
                    self.visited_commands.add(numeric_command)

                    print(f"{indent}Exploring numeric argument (sample): {numeric_command}")
                    sub_tree = self.map_commands(numeric_command, depth + 1, max_depth)
                    command_tree[str(s)] = sub_tree if sub_tree else {}
            else:
                for num in range(start, end + 1):
                    numeric_command = f"{base_command} {num}".strip()
                    if numeric_command in self.visited_commands:
                        continue
                    self.visited_commands.add(numeric_command)

                    print(f"{indent}Exploring numeric argument: {numeric_command}")
                    sub_tree = self.map_commands(numeric_command, depth + 1, max_depth)
                    command_tree[str(num)] = sub_tree if sub_tree else {}

        return command_tree

 
    def save_command_tree(self, command_tree, filename="12-2-55.json"):
        with open(filename, "w") as file:
            json.dump(command_tree, file, indent=4)
        print(f"Command tree saved to {filename}")
 
    def disconnect(self):
        if self.ssh_client:
            self.ssh_client.close()
 
# Example usage:
hostname = "10.60.112.119"
username = "nocansible"
password = "?a+Ltri3=e1aJO8!iDuP"
cisco_mapper = CiscoCommandMapper(hostname, username, password, max_range_size=3)
 
try:
    cisco_mapper.connect()
    command_tree = cisco_mapper.map_commands()
    print("Command mapping complete")
    cisco_mapper.save_command_tree(command_tree)
except Exception as e:
    print(f"Error: {e}")
finally:
    cisco_mapper.disconnect()