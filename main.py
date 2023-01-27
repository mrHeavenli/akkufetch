#!/bin/python3
import os
import upower
import json
import re

with open("config.json") as config_file:
    config = json.load(config_file)

upower_handler = upower.UPowerManager()
battery_info = upower_handler.get_full_device_information(config["BatteryPath"])
rounding_precision = int(config["rounding_precision"])

ANSI_REGEX = r"\x1B[\[()#;?]*(?:[0-9]{1,4}(?:;[0-9]{0,4})*)?[0-9A-ORZcf-nqry=><]"

def is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except:
        return False

def stripANSI(s: str) -> str: return re.sub(ANSI_REGEX, "", s)
def gen_image():
    battery_asciiart = ""
    percent = battery_info["Percentage"]
    
    fullchar_length = round((percent/100)*20)
    emptychar_length = 20-fullchar_length
    charge_bar = fullchar_length * config["chargechar"] + emptychar_length * config["emptychar"]

    battery_asciiart = "╔════════════════════╗\n║" \
                         + charge_bar \
                         + "╚╗\n║" \
                         + charge_bar \
                         + " ║\n║" \
                         + charge_bar \
                         + "╔╝" \
                         + "\n╚════════════════════╝"
    return battery_asciiart

j = 0
for i in gen_image().split("\n"):
    
    text = ""
    for l in config["lines"][j]:
        if l[0] == "!" and l.replace("!", "") in config["BatteryAttributesList"]:
            binfo = str(battery_info[l.replace("!", "")])
            if is_float(binfo):
                binfo = str(round(float(binfo), rounding_precision))
            text += binfo
    
        else:
            text +=l
    j += 1
    
    print(i+(23-len(stripANSI(i))+config["indent"])*" "+text)
          
    
    
        
