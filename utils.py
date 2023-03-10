# created by J. Cline (jordanc@ifit.com)
# as the name implies, utils.py provides useful utilities for the main program, some highly specific to scheduler.py
# TODO -> make exit error codes consistent (and have them make sense) -> extend to scheduler.py as well
# TODO -> code compaction

from subprocess import Popen, PIPE
from genericpath import isdir
from sys import path
from re import search
from time import sleep

# global formatted strings:
lin_star = "{0:*^50}".format("")
lin_dash = "{0:-^50}".format("")

#**********************************#

# runBashCommands: a function to handle running bash commands and piping back the results. Expects a list
def runBashCommands(bc_list):
    proc = Popen(bc_list[0].split(), stdout = PIPE)                                 # run a process with a given command, send output to PIPE
    for i in range(len(bc_list) - 1): proc = Popen(bc_list[i + 1].split(),\
        stdin = proc.stdout, stdout = PIPE)                                         # for each additional command pipe previous process' output to next process' input
    return proc.communicate()[0].rstrip().decode('ascii')                           # get data from proc PIPE, strip away whitespace, decode into ASCII; return value

# runProcess: a wrapper function for running processes; sleep if necessary
def runProcess(command):
    ps = Popen(command.split())                                                     # run a process with a given command
    ps.wait()                                                                       # wait for the command to finish

# this code block obtains the serial number and makes it globally available
global sn
sn_line = runBashCommands(["adb devices", "head -n2", "tail -n1"])
if type(sn_line) == str and sn_line.strip().replace('.', '').replace('\t', '').replace(':', '').isalnum() :
    sn = sn_line.split()[0]
    print(f"\nADB device {sn} detected\n")
else:
    print("\nNo ADB device detected... Quitting Program\n")
    exit()

adb_sn_gp = f"adb -s {sn} shell getprop"

# getAndroidVersion: gets the Android version from a tablet
def getAndroidVersion(): return runBashCommands([f"{adb_sn_gp} ro.build.version.release"])

# getTabletModel: get the model of the tabby
def getTabletModel(): return runBashCommands([f"{adb_sn_gp} ro.product.model"])

# getTabletVendor: get the vendor of the tabby (manufacturer, i.e. Malata, Compal, etc.)
def getTabletVendor(): return runBashCommands([f"{adb_sn_gp} ro.product.manufacturer"])

# getWolfVersion: returns the wolf version on the tabby
def getWolfVersion():
    version_name_raw = runBashCommands([f"adb -s {sn} shell dumpsys package com.ifit.standalone", "grep versionName"])
    version_code_raw = runBashCommands([f"adb -s {sn} shell dumpsys package com.ifit.standalone", "grep versionCode"])
    return (search(r'(\d.+)', version_name_raw).group(0)) + '.' + (search(r'[\d\.]+', version_code_raw).group(0))

# getAdminVersion: returns the admin version on the tabby
def getAdminVersion():
    version_name_raw = runBashCommands([f"adb -s {sn} shell dumpsys package com.ifit.eru", "grep versionName"])
    version_code_raw = runBashCommands([f"adb -s {sn} shell dumpsys package com.ifit.eru", "grep versionCode"])
    return (search(r'(\d.+)', version_name_raw).group(0)) + '.' + (search(r'[\d\.]+', version_code_raw).group(0))

# getOSVersion: returns the OS version of the tabby
def getOSVersion():
    return runBashCommands([f"adb -s {sn} shell getprop ro.build.version.incremental"])

# str_form: simplifies (and compacts) string formatting; codes: (c - centered; l - left)
def str_form(str, code, len):
    if code == 'c': return f"{{0:^{len}}}".format(str)
    if code == 'l': return f"{{0:<{len}}}".format(str)

# ttp: returns a double tabbed string
def ttp(str): return print(f"\t\t{str}")

# fsoCheck: checks for connection to full shell online (fso). If successful, returns True, if not, returns False
def fsoCheck(): return True if '1 packets transmitted, 1 packets received' in runBashCommands(['ping -c 1 fullshell01.iconfitness.com']) else False

# rootHandler: checks for root and then roots tablet, if necessary; racine is not included in the git project for security reasons
def rootHandler(sn, t_vendor):
    whoami_str = runBashCommands([f"adb -s {sn} shell whoami"])                                     # check to see if tablet is root or shell
    print(f"whoami_str: {whoami_str}")
    if whoami_str == "root":
        print("rootHandler: tablet is already rooted, proceeding with tests")
        return 1
    elif whoami_str == "shell":                                                                     # if not rooted, then root according the vendor rooting protocols (e.g. Malata or Compal)
        if isdir("./utils/racine"):
            path.append("./utils/racine")                                                       # add to system path so that importing is possible
            if t_vendor == "Malata":
                try: from racine import m_root_cmd as root_cmd                                      # import Malata instructions for rooting tablet
                except ModuleNotFoundError:
                    print("racine module not found at ./utils/racine/racine.py; "
                    "could not be imported")
                    return -1
            elif t_vendor("vendor") == "Compal":
                try: from racine import c_root_cmd as root_cmd
                except ModuleNotFoundError:
                        print("racine module not found at ./utils/racine/racine.py; "
                        "could not be imported")                   
                        return -1
            elif t_vendor("vendor") == "Eway": root_cmd = "Eway"
            else: 
                print("rootHandler: was not able to verify tablet vendor to root tablet, "
                "root manually and run again")
                return -1
        else:
            print("rootHandler: \"./utils/racine\" dir not found; obtain this module or "
            "root manually")
            return -1
        if root_cmd == "Eway":
            print("rootHandler: Eway does not currently root, proceeding with selected tests anyways")
            return 0
        for i in range(len(root_cmd)): runProcess(f"adb -s {sn} shell {root_cmd[i]}")
        sleep(3)
        whoami_str = runBashCommands([f"adb -s {sn} shell whoami"])
        if whoami_str == "root": return 1
        else: return -1
    else:
        print("rootHandler: could not verify tablet root status")
        return -1