class output:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    HIDDEN = "\033[8m"
    STRIKETHROUGH = "\033[9m"
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"
    BG_BRIGHT_BLACK = "\033[100m"
    BG_BRIGHT_RED = "\033[101m"
    BG_BRIGHT_GREEN = "\033[102m"
    BG_BRIGHT_YELLOW = "\033[103m"
    BG_BRIGHT_BLUE = "\033[104m"
    BG_BRIGHT_MAGENTA = "\033[105m"
    BG_BRIGHT_CYAN = "\033[106m"
    BG_BRIGHT_WHITE = "\033[107m"

    def error(string):
        print(output.RED + output.BOLD + str(string) + output.RESET)

    def info(string):
        print(output.BLUE + output.BOLD + str(string) + output.RESET)
        
    def warn(string):
        print(output.YELLOW + output.BOLD + str(string) + output.RESET)

import sys
import requests
import json
import os
import re
import time
from pathlib import Path

sec_forbidden = ["/", "\\", ".", "..","%2e", "%2f", "%5c","%252e", "%252f", "%255c","\x00", "%00",";", "&", "|", "`", "$", "!", "~", "*", "?", "<", ">","'", '"'," ", "\n", "\r", "\t","\u2024","\u2025","\uff0e","\u2215","\uff0f","\u29f5",":", "#", "@", "=", "+", "[", "]", "{", "}", "(", ")", "^", "%"]

slash = "\\" if os.name == "nt" else "/"
location = os.path.dirname(os.path.abspath(__file__)) + slash
with open(location + "settings.json", "r", encoding="utf-8") as f:
    settings = json.load(f)

if not settings["source"].lower().startswith("https://"):
    output.warn("conx security error: The source (in settings.json) doesnt have HTTPS.\nThis is a HUGE SECURITY RISK!!")
    exit(2)

if settings["type"] == "sudo":
    if os.name == "nt":
        path = Path.home() / "AppData" / "Local" / "Programs"
    else:
        path = Path("/usr/bin/")
elif settings["type"] == "local":
    if os.name == "nt":
        path = Path.home() / "AppData" / "Local" / "Programs"
    else:
        path = Path.home() / ".local" / "bin"

path = str(path)

del Path

info = {
    "version": 1.0,
    "credits": ["Charlie T"],
    "commands":[["help", "show a menu to guide you"], ["install", "install packages"], ["download", "download package to cwd"], ["version", "show the conx version"], ["list", "search the packages for a regex pattern"]]
}

# print(settings) # DEBUG



def list_pkgs(reg=""):
    if isinstance(reg, list):
        reg = reg[0] if reg else ""
    
    packages = requests.get(settings["source"] + settings["conxDB"]).text
    packages = json.loads(packages)
    
    def show_pkgs(list):
        num = 1
        for i in list:
            print(str(num) + ".  " + str(list))
            num += 1
    
    if reg == "":
        show_pkgs(packages)
    else:
        found = []
        for key in list(packages):
            #print(key)  # DEBUG
            if re.search(reg, str(key)):
                found.append(key)
        show_pkgs(found)

def download(arguments):
    if len(arguments) == 0:
        output.error("conx needs a package name to download.")
    else:
        packages = requests.get(settings["source"] + settings["conxDB"], verify=True).text
        packages = json.loads(packages)
        if not arguments[0] in packages:
            output.error("that package is not in the conx dB.")
        else:
            if any(char in packages[arguments[0]] for char in sec_forbidden):
                output.warn("conx security error: forbidden characters in name\n(to go against path traversal)\ntype --bypass to continue (!!NOT RECOMMENDED!!)")
                try:
                    if arguments[1].lower() == "--bypass":
                        output.error("ARE YOU SURE?? THIS CAN ALLOW AN ATTACKER TO CONTROL THE SYSTEM!\nFOR EXAMPLE, THEY COULD CHANGE YOUR PASSWORDS!!!")
                        time.sleep(1)
                        while True:
                            confirm = input("[y/n] ")
                            if confirm.lower() == "y" or confirm == "":break
                            elif confirm.lower() == "n":return
                except IndexError:return
            output.info("found package in dB. installing.")
            download = os.getcwd() + slash + packages[arguments[0]]
            output.info("downloading the file..")
            item = requests.get(settings["source"] + download, verify=True).text
            with open(download, "w") as file:
                file.write(item)
            print("conx finished downloading.\n")

def install(arguments):
    if len(arguments) == 0:
        output.error("conx needs a package name to install.")
    else:
        packages = requests.get(settings["source"] + settings["conxDB"], verify=True).text
        packages = json.loads(packages)

        if not arguments[0] in packages:
            output.error("that package is not in the conx dB.")
        else:
            if any(char in packages[arguments[0]] for char in sec_forbidden):
                output.error("conx security error: forbidden characters in name\n(to go against path traversal)\ntype --bypass to continue (!!NOT RECOMMENDED!!)")
                try:
                    if arguments[1].lower() == "--bypass":
                        output.error("ARE YOU SURE?? THIS CAN ALLOW AN ATTACKER TO CONTROL THE SYSTEM!\nFOR EXAMPLE, THEY COULD CHANGE YOUR PASSWORDS!!!")
                        time.sleep(1)
                        while True:
                            confirm = input("[y/n] ")
                            if confirm.lower() == "y" or confirm == "":break
                            elif confirm.lower() == "n":return
                except IndexError:return
            output.info("found package in dB. installing.")
            download = packages[arguments[0]]
            output.info("downloading the file..")
            item = requests.get(settings["source"] + download, verify=True).text
            output.info("installing the file..")
            with open(download, "w") as file:
                file.write(item)
            
            print("conx finished installing.\n")

def help():
    print("conx package manager v"+str(info["version"]))
    print("availible commands:\n")
    for i in info["commands"]:
        for x in i:
            print(x, end="   ")
        print()

def main():
    if len(sys.argv) <= 1:
        help()
    else:
        command = sys.argv[1].lower()
        args = sys.argv[2:]
        if command == "help":
            help()
        elif command == "version":
            print("conx package manager v"+str(info["version"]))
        elif command == "install":
            install(args)
        elif command == "download":
            download(args)
        elif command == "list":
            list_pkgs(args)
        elif command == "info":
            print("Settings:\n"+ str(settings))
            print("Info    :\n"+ str(info))
            print("File Sep:\n"+ slash)
            print("Location:\n"+ location)
            print("Path    :\n"+ path)
        else:
            print(output.BOLD + "that is not a valid conx operation.\ntype conx help for more info." + output.RESET)
        
if __name__ == "__main__":main() # Testing entrypoint