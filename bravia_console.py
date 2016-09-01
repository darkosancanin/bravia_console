#!/usr/bin/env python

import sys
import os
import time
import socket
import select
import re
import requests
import json
import collections

version = "1.0"

# python 2 compatibility
try: input = raw_input
except NameError: pass

def print_banner():
    def spaces(num):
        return " " * num
        
    banner = r"""

     ______                 _         _____                       _      
     | ___ \               (_)       /  __ \                     | |     
     | |_/ /_ __ __ ___   ___  __ _  | /  \/ ___  _ __  ___  ___ | | ___ 
     | ___ \ '__/ _` \ \ / / |/ _` | | |    / _ \| '_ \/ __|/ _ \| |/ _ \
     | |_/ / | | (_| |\ V /| | (_| | | \__/\ (_) | | | \__ \ (_) | |  __/
     \____/|_|  \__,_| \_/ |_|\__,_|  \____/\___/|_| |_|___/\___/|_|\___|
                                                                
    """
    banner += "\n\n" + spaces(28) + "Bravia Console\n\n"
    banner += spaces(28) + " Version: %s" % (version) + "\n"
    banner += spaces(23) + "Written by: " + "Darko Sancanin" + "\n"
    banner += spaces(25) + "Twitter: " + "@darkosan" + "\n"
    banner += spaces(20) + "https://github.com/darkosancanin" + "\n"
    print (banner)

print_banner()

class BraviaConsole:
    def __init__(self):
        self.psk = "0000"
        self.ip = None
        self.sys_info = {}
        self.commands = {}
        self.model = "Bravia"

    def print_status(self, message):
        print(("[*] ") + (str(message)))

    def print_info(self, message):
        print(("[-] ") + (str(message)))

    def print_warning(self, message):
        print(("[!] ") + (str(message)))

    def print_error(self, message):
        print(("[!] ") + (str(message)))
        
    def print_unauthorized_error(self):
        self.print_error("Error: Unauthorized. Please check you have configured the Pre-Shared Key correctly on the TV to %s." % self.psk)
        print("Instructions to setup PSK (Pre-Shared Key) on TV:")
        print("1. Navigate to: [Settings] -> [Network] -> [Home Network Setup] -> [IP Control]")
        print("2. Set [Authentication] to [Normal and Pre-Shared Key]")
        print("3. There should be a new menu entry [Pre-Shared Key]. Set it to '%s'" % self.psk)
        print("Note: To modify the PSK in this console enter 'set option psk <value>'")
        
    def show_help_menu(self):
        print("Commands:")
        print("{0:20} {1}".format("find tv", "Searches for the TV on the local LAN."))
        print("{0:20} {1}".format("configure", "Auto configures the console."))
        print("{0:20} {1}".format("show options", "Displays the current options and their values."))
        print("{0:20} {1}".format("set option <name>", "Manually changes a setting."))
        print("{0:20} {1}".format("update commands", "Updates the TV remote control commands."))
        print("{0:20} {1}".format("show commands", "Displays the TV remote control commands."))
        print("{0:20} {1}".format("search <command>", "Searches the TV remote control commands."))
        print("{0:20} {1}".format("update info", "Updates the system information."))
        print("{0:20} {1}".format("show info", "Displays the system information."))
        print("{0:20} {1}".format("quit", "Exits the console."))

    def exit_braviaremote(self):
        self.print_status("Exiting Bravia Remote.")
        sys.exit()
        
    def find_tv(self):
        self.print_info("Searching the local network for a Bravia TV")
        SSDP_ADDR = "239.255.255.250"
        SSDP_PORT = 1900

        ssdpRequest = "M-SEARCH * HTTP/1.1\r\n" + \
            "HOST: %s:%d\r\n" % (SSDP_ADDR, SSDP_PORT) + \
            "MAN: \"ssdp:discover\"\r\n" + \
            "MX: 1\r\n" \
            "ST: urn:schemas-sony-com:service:ScalarWebAPI:1\r\n\r\n";

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(5.0)
        dest = socket.gethostbyname(SSDP_ADDR)
        sock.sendto(ssdpRequest.encode('utf-8'), (dest, SSDP_PORT))
        sock.settimeout(5.0)
        try: 
            data = sock.recv(1000)
        except socket.timeout:
            self.print_error("No Sony Bravia TV found!")
            return
        response = data.decode('utf-8')
        match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", response)
        if match:                    
            self.ip = match.group()
            self.print_status("Bravia TV found at IP: %s" % self.ip)
        else:
            self.print_error("Unable to decode response")
            
    def update_commands(self):
        self.print_info("Updating commands")
        self.commands = {}
        result = self.send_info_request_to_tv("getRemoteControllerInfo")
        if result is not None:
            controller_commands = result[1]
            for command_data in controller_commands:
                self.commands[command_data.get('name').lower()] = command_data.get('value')
            self.commands = collections.OrderedDict(sorted(self.commands.items()))
            self.print_status("%d commands found" % len(self.commands))
        
    def show_commands(self):
        command_list = ""
        for command in self.commands:
            command_list += command + ", "
        if len(command_list) > 0: 
            command_list = command_list[:-2]
        self.print_info(command_list)
        
    def search_commands(self, search_string):
        command_list = ""
        for command in self.commands:
            if search_string in command:
                command_list += command + ", "
        if len(command_list) > 0: 
            command_list = command_list[:-2]
        self.print_info(command_list)
    
    def update_sys_info(self):
        self.print_info("Updating system info")
        if self.ip is None:
            self.print_error("TV was not found. Please run configure first")
            return
        result = self.send_info_request_to_tv("getSystemInformation")
        if result is not None:
            self.sys_info = result[0]
            self.model = self.sys_info["model"]
            self.print_status("TV model identified as %s" % self.model)
        
    def show_sys_info(self):
        for info in self.sys_info:
            self.print_info("%s: %s" % (info, self.sys_info[info]))
            
    def send_info_request_to_tv(self, command):
        body = {"method": command, "params": [], "id": 1, "version": "1.0"}
        json_body = json.dumps(body).encode('utf-8')
        headers = {}
        headers['X-Auth-PSK'] = self.psk
        try:
            response = requests.post('http://' + self.ip + '/sony/system', headers=headers, data=json_body, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as exception_instance:
            if response.status_code == 403:
                self.print_unauthorized_error()
            else:
                self.print_error("Exception: " + str(exception_instance))
            return None
        except Exception as exception_instance: 
            self.print_error("Exception: " + str(exception_instance))
            return None
        else:
            return json.loads(response.content.decode('utf-8'))["result"]
            
    def send_command_to_tv(self, command):
        if command not in self.commands:
            return False;
        ircc_code = self.commands[command]
        self.print_status("Sending command %s to TV" % command)
        body = "<?xml version=\"1.0\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:X_SendIRCC xmlns:u=\"urn:schemas-sony-com:service:IRCC:1\"><IRCCCode>" + ircc_code + "</IRCCCode></u:X_SendIRCC></s:Body></s:Envelope>"
        headers = {}
        headers['X-Auth-PSK'] = self.psk
        headers['Content-Type'] = "text/xml; charset=UTF-8"
        headers['SOAPACTION'] = "\"urn:schemas-sony-com:service:IRCC:1#X_SendIRCC\""
        try:
            response = requests.post('http://' + self.ip + '/sony/IRCC', headers=headers, data=body, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as exception_instance:
            if response.status_code == 403:
                self.print_unauthorized_error()
            else:
                self.print_error("Exception: " + str(exception_instance))
        except Exception as exception_instance: 
            self.print_error("Exception: " + str(exception_instance))  
        return True
            
    def auto_configure(self):
        self.print_info("Auto detecting settings")
        self.find_tv()
        if self.ip is not None:
            self.update_sys_info()
            self.update_commands()
        else:
            self.print_error("Auto configuration failed, enter the command 'configure' to try again")
            
    def show_options(self):
        print("{0:7} {1:20} {2}".format("psk: ", self.psk, "(Pre shared key)"))
        print("{0:7} {1:20} {2}".format("ip: ", self.ip, "(IP address)"))
        
    def set_option(self, option_name_value):
        if option_name_value.startswith("psk "):
            psk = option_name_value[4:]
            self.psk = psk
            self.print_info("PSK set to %s." % self.psk)
        elif option_name_value.startswith("ip "):
            match = re.search(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", option_name_value)
            if match:                    
                self.ip = match.group()
                self.print_info("IP set to %s" % self.ip)
            else:
                self.print_error("Invalid ip value")
        else:
            self.print_error("Invalid option value")
    
    def signal_handler(self, signal, frame):
        print("")
        self.exit_braviaremote()
       
    def start(self):
        self.auto_configure()
        while 1:
            try:
                prompt = input(self.model + "> ")
            except EOFError:
                prompt = "quit"
                print("")

            if prompt == "?" or prompt == "help":
                self.show_help_menu()
                continue
                
            if prompt == "configure":
                self.auto_configure()
                continue
                
            if prompt == "find tv":
                self.find_tv()
                continue
                
            if prompt == "update commands":
                self.update_commands()
                continue
                
            if prompt == "show commands":
                self.show_commands()
                continue
            
            if prompt == "show info":
                self.show_sys_info()
                continue
                
            if prompt == "show options":
                self.show_options()
                continue
                
            if prompt == "update info":
                self.update_sys_info()
                continue
                
            if prompt.startswith("search"):
                search_string = prompt[6:].strip()
                self.search_commands(search_string)
                continue
                
            if prompt.startswith("set option"):
                option_name_value = prompt[10:].strip()
                self.set_option(option_name_value)
                continue

            if prompt == "quit" or prompt == "exit":
                self.exit_braviaremote()
                
            if self.send_command_to_tv(prompt):
                continue

            self.print_warning("Command was not found, try help or ? for more information")
   
def main():
    console = BraviaConsole()
    console.start()
    

if __name__ == "__main__":
	main()