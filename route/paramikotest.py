import paramiko
import time

def execute_ssh_command(ip, username, password, command):
    try:
        # Create an SSH client
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the server
        ssh.connect(ip, username=username, password=password)

        # Open a session and get a channel
        channel = ssh.get_transport().open_session()
        channel.get_pty()
        time.sleep(1)  # Adding a small delay to allow terminal initialization

        # Execute the command
        stdin, stdout, stderr = channel.exec_command(command)

        # Print the output
        print("Output:")
        for line in stdout.readlines():
            print(line.strip())

        print("Errors:")
        for line in stderr.readlines():
            print(line.strip())

        # Close the connection
        ssh.close()
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Replace these with your server's IP, username, and password
    ip_address = "10.232.62.130"
    username = "admin"
    password = "Quick5and"
    command = "show ?"

    execute_ssh_command(ip_address, username, password, command)
