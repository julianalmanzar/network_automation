import paramiko
import time
import re

'''
This function creates a SSH connection to a Device.
host is a dictionary that has the following structure:
host = {'hostname': 'IP or HOSTNAME', 'port': '22', 'username': 'username', 'password': 'passwd'}
'''


def create_connection(host):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**host, look_for_keys=False, allow_agent=False)
    cli = ssh.invoke_shell()
    return ssh, cli


'''This function reads the output of the cli of a connection
I created this for the sole purpose of having a shorter way
to write the read command on the rest of the code.
'''


def read_output(cli):
    message = cli.recv(1000000000000000000000000).decode('utf-8')
    return message


'''
This function makes a lookup on the MAC Address Table
for the port where the provided mac address is learned from.

host is a dictionary that has the following structure:
host = {'hostname': 'IP or HOSTNAME', 'port': '22', 'username': 'username', 'password': 'passwd'}

You need to know how to find a mac addres in the target device.

The MAC address needs to be provided in the same format the switch supports.

The search command should be written as you would do on the console just without the MAC.

The port_regexp is a regluar expression that needs to match the names of all the possible interface
names on the switch.
'''


def get_port_mac(host, mac, search_command, port_regexp):
    try:
        ssh, cli = create_connection(host)
        cli.send(f'{search_command} {mac}\n')
        time.sleep(5)
        message = read_output(cli)
        port = re.findall(port_regexp, message, flags=re.IGNORECASE)
        ssh.close()
    except IndexError:
        print(host['hostname'] + " not available\n")
    return port[0]


'''
This function helps us to get the uplink of a network device using 
the gateway IP and ARP for this.

host is a dictionary that has the following structure:
host = {'hostname': 'IP or HOSTNAME', 'port': '22', 'username': 'username', 'password': 'passwd'}

The arp_search_command should be the search command you type o the device console when
searching for an ARP record, just without the IP.

The mac_search_command should be written as you would do on the console just without the MAC.

The port_regexp is a regluar expression that needs to match the names of all the possible interface
names on the switch.

What happens here is basically we add 1 command to the search and reuse the get_mac_port function
'''


def get_uplink(host, gateway, arp_search_command, mac_search_command, port_regexp):
    try:
        ssh, cli = create_connection(host)
        cli.send(f'{arp_search_command} {gateway}\n')
        time.sleep(5)
        arp = read_output(cli)
        mac = re.findall('(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})', arp)
        ssh.close()
        port = get_port_mac(host, mac[0], mac_search_command, port_regexp)
    except IndexError:
        print(host['hostname'] + " not available\n")
    return port


'''
This function executes a single command directly on the target device and returns
the console output.

host is a dictionary that has the following structure:
host = {'hostname': 'IP or HOSTNAME', 'port': '22', 'username': 'username', 'password': 'passwd'}

Command should be a string
'''


def execute_command(host, command):
    try:
        ssh, cli = create_connection(host)
        cli.send(command + "\n")
        time.sleep(5)
        message = read_output(cli)
        ssh.close()
    except Exception as e:
        print(f"Error at: {host} ------> {e}".format(hostname=host, error=e))
    return message


'''
This function executes a list of commands on the target device.

host is a dictionary that has the following structure:
host = {'hostname': 'IP or HOSTNAME', 'port': '22', 'username': 'username', 'password': 'passwd'}

commands should be a list of strings
'''


def execute_bulk_commands(host, commands):
    try:
        ssh, cli = create_connection(host)
        for command in commands:
            cli.send(command + "\n")
            time.sleep(2)
        ssh.close()
    except Exception as e:
        print(f"Error at: {host} ------> {e}".format(hostname=host, error=e))
