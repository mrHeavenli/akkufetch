#!/usr/bin/python3

import argparse

from dbus_handler import Battery
from config import Config
from akkufetch import Akkufetch

parser = argparse.ArgumentParser(prog="akkufetch", description="neofetch for batteries",)
parser.add_argument("-c", "--config", default=None, metavar="path", help="Path to config file")
parser.add_argument("--no-ansii", action="store_true", help="Disable ansii colors")
parser.add_argument("--generate-config", action="store_true", help="Generate config file and exits")
args = parser.parse_args().__dict__

if args["generate_config"]:
    Config.generate_config()
    exit("Generated config file at ~/.config/akkufetch.toml")

cfg_override = {}
if args["no_ansii"]:
    cfg_override["colors.charged"] = ""
    cfg_override["colors.reset"] = ""
    cfg_override["colors.dynamic"] = False

config = Config(args["config"], cfg_override)
battery = Battery(config["battery_path"], config)
config.generate_dynamic(battery["Percentage"])

print(Akkufetch((config["battery_art.height"], config["battery_art.width"], config["battery_art.horizontal"]), battery, config))
