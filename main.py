#!/bin/python3
import os
import upower
import json
from colorama import Fore, Back, Style

with open("config.json") as config_file:
    config = json.load(config_file)

upower_handler = upower.UPowerManager()
binfo = upower_handler.get_full_device_information(config["BatteryPath"])

percent = binfo["Percentage"]

fullchar_length = round((percent/100)*20)
emptychar_length = 20-fullchar_length
charge_bar = fullchar_length * config["chargechar"]

if config["barcolourchanger"]:

    # change bar color depending on the battery percentage
    if percent > 40:   charge_bar = Fore.GREEN + charge_bar + Style.RESET_ALL
    elif percent > 20: charge_bar = Fore.YELLOW + charge_bar + Style.RESET_ALL
    else:              charge_bar = Fore.RED + charge_bar + Style.RESET_ALL

charge_bar += emptychar_length * config["emptychar"]

battery_asciiart = f"""\
╔════════════════════╗ 
║{charge_bar}╚╗
║{charge_bar} ║
║{charge_bar}╔╝
╚════════════════════╝ 
"""
battery_asciiart += ((' '*23) + '\n')*round(len(config['display_info'])-5) 


try:
    for idx, line in enumerate(battery_asciiart.split('\n')[:-1]):
        print(line, end=' '*config["indent"])
        for l in config["display_info"][idx]:
            if l[0] == '!':
                if str(type(binfo[l[1:]])) != "<class 'dbus.String'>":
                    print(str(round(binfo[l[1:]], config["rounding_precision"])), end="")
                    continue
                print(str(binfo[l[1:]]), end="")
            else:
                print(l, end="")
        print()
except IndexError:
    pass
print()