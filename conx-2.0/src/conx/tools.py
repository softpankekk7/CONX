# Source - https://stackoverflow.com/a/16876405
# Posted by PSS, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-11, License - CC BY-SA 4.0

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
import zipfile
import hashlib
import shutil
import subprocess

sec_forbidden = ["/", "\\", "..","%2e", "%2f", "%5c","%252e", "%252f", "%255c","\x00", "%00",";", "&", "|", "`", "$", "!", "~", "*", "?", "<", ">","'", '"'," ", "\n", "\r", "\t","\u2024","\u2025","\uff0e","\u2215","\uff0f","\u29f5",":", "#", "@", "=", "+", "[", "]", "{", "}", "(", ")", "^", "%"]

slash = "\\" if os.name == "nt" else "/"
location = os.path.dirname(os.path.abspath(__file__)) + slash


installed_packs = set()


try:
    with open(location + "settings.json", "r", encoding="utf-8") as f:
        settings = json.load(f)
except FileNotFoundError:
    output.error("conx error: settings.json not found.")
    sys.exit(1)
except json.JSONDecodeError:
    output.error("conx error: settings.json is not valid JSON.")
    sys.exit(1)


required_keys = ["source", "conxDB"]
missing_keys = [key for key in required_keys if key not in settings]
if missing_keys:
    output.error(f"conx error: Missing required settings: {', '.join(missing_keys)}")
    sys.exit(1)

if not settings["source"].lower().startswith("https://"):
    output.warn("conx security error: The source (in settings.json) doesnt have HTTPS.\nThis is a HUGE SECURITY RISK!!")
    exit(2)

info = {
    "version": 2.0,
    "credits": ["Charlie T"],
    "commands":[["help", "show a menu to guide you"], ["install", "install packages"], ["version", "show the conx version"], ["list", "search the packages for a regex pattern"]]
}

def clear_line():
    sys.stdout.write('\033[A\033[K')
    sys.stdout.flush()

def list_pkgs(reg=""):
    if isinstance(reg, list):
        reg = reg[0] if reg else ""
    
    
    try:
        
        source_url = settings["source"]
        if not source_url.endswith("/"):
            source_url += "/"
        packages = requests.get(source_url + settings["conxDB"]).text
        packages = json.loads(packages)
    except requests.RequestException as e:
        output.error(f"conx error: Failed to fetch package list: {e}")
        return
    except json.JSONDecodeError:
        output.error("conx error: Invalid package database format.")
        return
    
    def show_pkgs(list):
        num = 1
        for i in list:
            
            print(str(num) + ".  " + str(i))
            num += 1
    
    if reg == "":
        show_pkgs(packages)
    else:
        found = []
        for key in list(packages):
            if re.search(reg, str(key)):
                found.append(key)
        show_pkgs(found)

def install(arguments):
    if len(arguments) == 0:
        output.error("conx needs a package name to install.")
        return
    
    package_name = arguments[0]
    
    
    if package_name in installed_packs:
        output.info(f"Package '{package_name}' already installed, skipping.")
        return
    
    download = None  
    
    try:
        
        source_url = settings["source"]
        if not source_url.endswith("/"):
            source_url += "/"
        packages = requests.get(source_url + settings["conxDB"], verify=True).text
        packages = json.loads(packages)
    except requests.RequestException as e:
        output.error(f"conx error: Failed to fetch package database: {e}")
        return
    except json.JSONDecodeError:
        output.error("conx error: Invalid package database format.")
        return

    if not arguments[0] in packages:
        output.error("that package is not in the conx dB.")
        return
    
    if any(char in packages[arguments[0]] for char in sec_forbidden):
        output.error("conx security error: forbidden characters in name\n(to go against path traversal)\ntype --bypass to continue (!!NOT RECOMMENDED!!)")
        try:
            if arguments[1].lower() == "--bypass":
                output.error("ARE YOU SURE?? THIS CAN ALLOW AN ATTACKER TO CONTROL THE SYSTEM!\nFOR EXAMPLE, THEY COULD CHANGE YOUR PASSWORDS!!!")
                time.sleep(1)
                while True:
                    confirm = input("[y/n] ")
                    
                    if confirm.lower() == "y":
                        break
                    elif confirm.lower() == "n" or confirm == "":
                        return
        except IndexError:
            return
    
    output.info("found package in dB. installing.")
    download = packages[arguments[0]]
    output.info("downloading the file..")
    
    
    try:
        
        source_url = settings["source"]
        if not source_url.endswith("/"):
            source_url += "/"
        
        response = requests.get(source_url + download, verify=True)
        response.raise_for_status()
        item = response.content
    except requests.RequestException as e:
        output.error(f"conx error: Failed to download package: {e}")
        return
    
    output.info("installing the file..")
    
    try:
        with open(download, "wb") as file:
            file.write(item)
    except IOError as e:
        output.error(f"conx error: Failed to write package file: {e}")
        return
    
    output.info("extracting the package..")
    
    extract_to = os.getcwd() + "/package/"

    try:
        with zipfile.ZipFile(download, 'r') as package:
            members = package.namelist()
            
            if members:
                first_components = set()
                for member in members:
                    parts = member.split('/')
                    if len(parts) > 1:
                        first_components.add(parts[0])
                
                if len(first_components) == 1:
                    root_dir = first_components.pop() + '/'
                    for member in package.namelist():
                        if member == root_dir:
                            continue
                        
                        if member.startswith(root_dir):
                            target_path = member[len(root_dir):]
                            if target_path:  
                                source = package.open(member)
                                target = os.path.join(extract_to, target_path)
                                os.makedirs(os.path.dirname(target), exist_ok=True)
                                if not member.endswith('/'):
                                    with open(target, 'wb') as f:
                                        f.write(source.read())
                                source.close()
                else:
                    package.extractall(extract_to)
            else:
                output.error("conx error: package is empty.")
                return
    except zipfile.BadZipFile:
        output.error("conx error: Downloaded file is not a valid ZIP archive.")
        return
    except IOError as e:
        output.error(f"conx error: Failed to extract package: {e}")
        return
    
    output.info("Generating bubblewrap settings..")
    try:
        with open("package" + slash + "bubblewrap.json", "r", encoding="utf-8") as f:
            pack_settings = json.load(f)
    except FileNotFoundError:
        output.error("conx error: bubblewrap.json not found in package.")
        return
    except json.JSONDecodeError:
        output.error("json error: JSONDecodeError. Yikes!")
        return

    output.info("Checking checksums..")

    if "install-hash" not in pack_settings:
        output.error("conx error: bubblewrap.json does not have install-hash.")
        return
    elif pack_settings["install-hash"].strip() == "":
        output.warn("conx warning: bubblewrap.json has NO HASH. Package may be malformed or malicious.\n^Z or ^C to stop.")
        for i in range(5, 0, -1):
            print(i)
            time.sleep(1)
            clear_line()
    else:
        install_file_path = os.path.join("package", pack_settings["install"])
        
        if not os.path.exists(install_file_path):
            output.error(f"conx error: {pack_settings['install']} not found in package")
            return
        
        with open(install_file_path, 'rb') as file_to_check:
            data = file_to_check.read()
            if pack_settings["install-hash"].strip() == hashlib.sha256(data).hexdigest():
                output.info("Checksum verified. Continue.")
            else:
                output.error("conx ERROR! Checksum verification failed!")
                return

    if "dependencies" not in pack_settings:
        output.error("conx error: bubblewrap.json missing 'dependencies' field")
        return
    
    
    for package_dep in pack_settings["dependencies"]:
        if package_dep != arguments[0]:
            install([package_dep])
    
    if "install" not in pack_settings:
        output.error("conx error: bubblewrap.json missing 'install' field")
        return
    
    install_path = pack_settings["install"]
    
    
    if any(char in install_path for char in sec_forbidden):
        output.error("conx security error: installer path contains forbidden characters")
        return
    
    
    full_install_path = os.path.join("package", install_path)
    if not os.path.exists(full_install_path):
        output.error(f"conx error: {install_path} not found in package")
        return
    
    
    if not os.path.abspath(full_install_path).startswith(os.path.abspath("package")):
        output.error("conx security error: install path attempts to escape package directory")
        return

    output.info("Using defined installer..")

    try:
        
        result = subprocess.run(
            [sys.executable, install_path],
            capture_output=True,
            text=True,
            timeout=300,
            check=True,
            cwd=os.path.join(os.getcwd(), "package")
        )
        
        if result.stdout:
            print(result.stdout)
        
        output.info("Installation completed successfully")
        
    
    except subprocess.TimeoutExpired:
        output.error("Installation script timed out after 5 minutes")
        return
    except subprocess.CalledProcessError as e:
        output.error(f"Installation script failed with exit code {e.returncode}")
        if e.stderr: 
            print("Error output:", e.stderr)
        return
    except FileNotFoundError:
        output.error(f"conx error: {install_path} not found in package")
        return
    except Exception as e:
        output.error(f"conx error: install error: {e}")
        return
    finally:
        
        output.info("Cleaning up temporary files..")
        try:
            if os.path.exists("package"):
                shutil.rmtree("package")
        except Exception as e:
            output.warn(f"Warning: Failed to remove package directory: {e}")
        
        try:
            if download and os.path.exists(download):
                os.remove(download)
        except Exception as e:
            output.warn(f"Warning: Failed to remove download file: {e}")
    
    
    installed_packs.add(package_name)
    
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
            
            installed_packs.clear()
            install(args)
        elif command == "list":
            list_pkgs(args)
        elif command == "info":
            print("Settings:\n"+ str(settings))
            print("Info    :\n"+ str(info))
            print("File Sep:\n"+ slash)
            print("Location:\n"+ location)
        else:
            print(output.BOLD + "that is not a valid conx operation.\ntype conx help for more info." + output.RESET)
        
if __name__ == "__main__":main()