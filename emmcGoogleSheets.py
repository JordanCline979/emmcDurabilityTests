# for uploading tablet results to a Google Sheet

import pygsheets
import datetime

class googleSheetsTablet:

    # connect: function that connects to google sheet
    def connect(self):
        GoogleSheet = pygsheets.authorize(service_account_file='./creds/fstabtracker-1306e591bd99.json')    # authorizing script to access google sheet
        self.MasterListSheet = GoogleSheet.open('Extended eMMC CMD56 Testing')    # opening google sheet 'Extended eMMC CMD56 Testing'

    # initialize_data: runs once to add tablet-specific data to the sheet
    def initialize_data(self, serial, model, os_v, android_v, wolf_v, admin_v):
        # find first empty column
        MainSheet = self.MasterListSheet.worksheet_by_title('Data')    # selecting the Data sheet
        self.col_oi = MainSheet.get_row(1, 'matrix').index('') + 1

        val_arr = [serial, model, os_v, android_v, wolf_v, admin_v]

        #change this to "update_values()" -> cleaner and more efficient
        for i in range(1, 7):
            MainSheet.update_value((i, self.col_oi), val_arr[i - 1])
            MainSheet.update_value((i, self.col_oi + 1), "-")

        MainSheet.cell((7, self.col_oi)).set_text_format('bold', True).value = 'P/E Cycles (Hex)'
        MainSheet.cell((7, self.col_oi + 1)).set_text_format('bold', True).value = '1 MB Block Writes (Hex)'

        self.row_oi = 8

    # update: updates the 'Extended eMMC CMD56 Testing' Google sheet
    def update(self, pe_cycles, num_writes):
        try:
            MainSheet = self.MasterListSheet.worksheet_by_title('Data')    # selecting the Data sheet
            MainSheet.update_value((self.row_oi, self.col_oi), pe_cycles)
            MainSheet.update_value((self.row_oi, self.col_oi + 1), num_writes)
            self.row_oi += 1

        except: print('googleSheetsTablet->upload(): Was unable to upload tablet data to google sheets')

global tabTrackingDict
key_list = ["date", "model", "size", "vendor", "android_version", "os_version", "chipset", "gpu_chip", "wifi_level", "wifi_speed_down", "wifi_speed_up", "req_storage_GB", "rep_storage_GB", "req_data_part_GB", "rep_data_part_GB", "req_RAM_GB", "rep_RAM_GB", "sec_patch_level", "html5_score"]
tabTrackingDict = dict.fromkeys(key_list)
global google_tablet
google_tablet = googleSheetsTablet()