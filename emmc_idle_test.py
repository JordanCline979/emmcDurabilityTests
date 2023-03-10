#! /usr/local/bin/python3

from utils import runBashCommands, sn, rootHandler, getOSVersion, getAndroidVersion, getTabletModel, getTabletVendor, getWolfVersion, getAdminVersion
from emmcGoogleSheets import google_tablet
from time import sleep

t_vendor = getTabletVendor()
t_model = getTabletModel()
t_osversion = getOSVersion()
t_anversion = getAndroidVersion()
t_wolfVersion = getWolfVersion()
t_adminVersion = getAdminVersion()

# root the tabby
print("rooting tablet...")
rootHandler(sn, t_vendor)

emmc_id_dict = dict([('008GB0', 'Xioxia'), ('008G70', 'Xioxia')])
emmc_vendor_code = runBashCommands([f"adb -s {sn} shell cat /sys/class/block/mmcblk0/device/name"])

if emmc_vendor_code not in emmc_id_dict:
    print(f"eMMC {emmc_vendor_code} is untracked in this program. Aborting...\n")
    exit(1)
if emmc_id_dict[emmc_vendor_code]== 'Xioxia': print("Xioxia eMMC detected, proceeding with tests")
else:
    print("Xioxia eMMC not detected, other eMMC vendors not currently supported\naborting program...\n")
    exit(1)

google_tablet.connect()
google_tablet.initialize_data(sn, t_model, t_osversion, t_anversion, t_wolfVersion, t_adminVersion)

f = open("emmc_results.dat", "a")

while 1:
    emmc_data = runBashCommands([f"adb -s {sn} shell /data/local/tmp/mmc gen_cmd read /dev/block/mmcblk0"]).split()
    
    for i in range(9, 13):
        if len(emmc_data[i]) == 1: emmc_data[i] = '0' + emmc_data[i]
    for i in range(562, 566):
        if len(emmc_data[i]) == 1: emmc_data[i] = '0' + emmc_data[i]
    erase_cnt = f"{emmc_data[9]}{emmc_data[10]}{emmc_data[11]}{emmc_data[12]}\n"
    c_writes = f"{emmc_data[562]}{emmc_data[563]}{emmc_data[564]}{emmc_data[565]}\n"

    google_tablet.update(erase_cnt, c_writes)

    sleep(3600)

f.close()

#run the login sequence
runBashCommands(["./auto_engine.py start_to_dash.dat"])