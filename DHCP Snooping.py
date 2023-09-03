import threading
import net_tools

'''
Creating all of the parameter for each device brand
in my case I had these but they could be different in your case.
'''

cisco_switches = ["cisco_switch_01", "cisco_switch_02"]
cisco_switches_arp_search = "show arp ip-address "
cisco_switches_mac_search = "show mac address-table address "
cisco_switches_port_regexp = "gi[0123456789].{1,5}|fa[0123456789].{1,5}"

fortiswitches = ["fortiswitch_01", "fotiswitch_02"]
fortiswitches_arp_search = "diagnose ip arp list | grep "
fortiswitches_mac_search = "diagnose switch mac-address list | grep "
fortiswitches_port_regexp = "port[0-9]{1,2}"

# Creating the connection information. We´ll substitute the hostname later

connection_info = {'hostname': "",
                   'port': '22',
                   'username': 'username',
                   'password': 'password'}

gateway = "172.20.90.1"

cisco_switches_threads = list()
for hostname in cisco_switches:
    # We substitute the value of the hostname in the dictionary to match the target device
    # and we create a thread for each switch so the commands can be executed faster using multi-threading
    connection_info['hostname'] = hostname
    uplink_port = net_tools.get_uplink(connection_info, gateway, cisco_switches_arp_search,
                                       cisco_switches_mac_search, cisco_switches_port_regexp)
    cisco_switches_commands = ["enable",
                               "configure terminal",
                               "ip dhcp snooping",
                               "ip dhcp snooping database",
                               "ip dhcp snooping vlan 1",
                               f"interface {uplink_port}",
                               "ip dhcp snooping trust",
                               "end",
                               "wr",
                               "Y"]
    th = threading.Thread(target=net_tools.execute_bulk_commands, args=(connection_info, cisco_switches_commands))
    cisco_switches_threads.append(th)

fortiswitches_threads = list()
for hostname in fortiswitches:
    # We substitute the value of the hostname in the dictionary to match the target device
    # and we create a thread for each switch so the commands can be executed faster using multi-threading
    connection_info['hostname'] = hostname
    uplink_port = net_tools.get_uplink(connection_info, gateway, fortiswitches_arp_search,
                                       fortiswitches_mac_search, fortiswitches_port_regexp)
    fortiswitches_commands = ["config switch vlan",
                              "edit 1",
                              "set dhcp-snooping enable",
                              "end",
                              "config switch interface",
                              f"edit {uplink_port}",
                              "set dhcp-snooping trusted",
                              "end"]
    th = threading.Thread(target=net_tools.execute_bulk_commands, args=(connection_info, fortiswitches_commands))
    fortiswitches_threads.append(th)


# We start our threads
for thread in cisco_switches_threads:
    thread.start()

for thread in fortiswitches_threads:
    thread.start()

# We wait for all of them to finish
for thread in cisco_switches_threads:
    th.join()

for thread in fortiswitches_threads:
    th.join()