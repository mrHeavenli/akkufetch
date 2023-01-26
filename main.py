#!/bin/python3
import os
import upower
import json

with open("config.json") as config_file:
    config = json.load(config_file)

upower_handler = upower.UPowerManager()
battery_info = upower_handler.get_full_device_information(config["BatteryPath"])


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
            
            text += str(battery_info[l.replace("!", "")])
    
        else:
            text +=l
    j += 1

    print(i+(23-len(i)+config["indent"])*" "+text)
          
    
    
        