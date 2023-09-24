from os.path import isfile, expanduser
from tomllib import load, TOMLDecodeError
from json import load as json_load, JSONDecodeError

CONFIG_FILENAME = "akkufetch.toml"
USER_CONFIG = expanduser(f"~/.config/{CONFIG_FILENAME}")
SYSTEM_CONFIG = f"/etc/{CONFIG_FILENAME}"
FALLBACK_CONFIG = f"{__file__.removesuffix('/config.py')}/../examples/{CONFIG_FILENAME}"


class Config:
    def __init__(self, path: str or None, override=None):
        self.override = override or {}
        paths = []

        if path:
            if not isfile(path): exit(f"Config file at '{path}' not found")
            paths.append(path)

        if isfile(USER_CONFIG): paths.append(USER_CONFIG)
        if isfile(SYSTEM_CONFIG): paths.append(SYSTEM_CONFIG)

        paths.append(FALLBACK_CONFIG)

        self.configs = []
        for path in paths:
            with open(path, 'rb') as f:
                try: self.configs.append(load(f))
                except TOMLDecodeError as e:
                    try:
                        json = self._translate_old_config(json_load(f))
                        self.configs.append(json)

                        print(f"Warning: JSON config files are deprecated. Please convert {path} to TOML.")

                    except JSONDecodeError: exit(f"Failed at parsing {path}: \n{e.args[0]}")

    def __getitem__(self, items):
        if items in self.override: return self.override[items]
        items = items.split('.')

        for config in self.configs:
            for i, item in enumerate(items):
                if item in config:
                    if i == len(items)-1: return config[item]

                    if type(config[item]) == dict:
                        config = config[item]
                        continue

                    break

        raise KeyError(f"Key '{'.'.join(items)}' not found in any config file. Is the fallback config bricked?")

    def generate_dynamic(self, percentage):
        if "dynamic" in self["colors"] and self["colors.dynamic"]:
            configured = False
            for setting in self["colors.dynamic"]:
                if percentage in range(setting[0], setting[1]):
                    self.override["colors.charged"] = setting[2]
                    configured = True
                    break

            if not configured: raise KeyError(f"'colors.dynamic_colors' is incorrectly configured. Percentage {int(percentage) if int(percentage) == percentage else percentage} not configured.")

        if "dynamic" in self["battery_art"] and self["battery_art.dynamic"]:
            amount = len(self["system_info.format"])

            if amount >= 7:
                self.override["battery_art.height"] = amount
                self.override["battery_art.width"] = round(amount * 1.375)
                self.override["battery_art.horizontal"] = True
            else:
                self.override["battery_art.height"] = round(amount * 3.4)
                self.override["battery_art.width"] = amount
                self.override["battery_art.horizontal"] = False

    @staticmethod
    def _translate_old_config(config: {}):
        translated = {"chars": {}, "system_info": {}, "colors": {}}

        for key, value in config.items():
            match key:
                case "chargechar": translated["chars"]["charge"] = value
                case "emptychar": translated["chars"]["empty"] = value

                case "indent": translated["system_info"]["indent"] = value
                case "rounding_precision": translated["system_info"]["rounding_precision"] = value

                case "display_info": translated["system_info"]["display_info"] = ["".join(item).replace('!', '$') for item in value]

                case "barcolourchanger":
                    if value:
                        translated["colors"]["dynamic"] = [
                            [0, 20, "\u001b[31m"],
                            [20, 40, "\u001b[33m"],
                            [40, 100, "\u001b[32m"],
                        ]

        return translated

    @staticmethod
    def generate_config():
        try:
            with open(USER_CONFIG, "x"): pass
        except FileExistsError: exit(f"Config file at {USER_CONFIG} already exists.")

        with open(USER_CONFIG, "wt") as f:
            f.write(open(FALLBACK_CONFIG, "rt").read())
